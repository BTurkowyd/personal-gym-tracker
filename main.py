import boto3
import json
from langchain_core.tools import tool
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated, TypedDict


region = "eu-central-1"
bedrock_client = boto3.client("bedrock-runtime", region_name=region)

# Claude 3 via Bedrock
llm = ChatBedrock(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    region=region,
)

lambda_client = boto3.client("lambda", region_name=region)

# Cache for tool results to avoid repeated calls
_tool_cache = {}


@tool
def get_glue_table_schema(input: str) -> str:
    """Return schemas for workouts, exercises, and sets tables: table name, column names, types, and comments."""
    cache_key = "glue_schema"
    if cache_key in _tool_cache:
        return _tool_cache[cache_key]

    response = lambda_client.invoke(FunctionName="GetGlueTableSchema", Payload=b"{}")
    payload = json.loads(response["Payload"].read().decode("utf-8"))

    # The lambda now returns a dict with keys: workouts, exercises, sets
    body = payload.get("body") or json.loads(payload["body"])
    if isinstance(body, str):
        body = json.loads(body)

    result = []
    for label in ["workouts", "exercises", "sets"]:
        table = body[label]
        table_name = table["table_name"]
        columns = table["columns"]
        data_types = "\n".join(f"- {col['name']}: {col['type']}" for col in columns)
        comments = "\n".join(
            f"- {col['name']}: {col.get('comment', 'no comment')}" for col in columns
        )
        result.append(
            f"Table `{table_name}` ({label}):\nData Types:\n{data_types}\nComments:\n{comments}"
        )

    _tool_cache[cache_key] = "\n\n".join(result)
    return _tool_cache[cache_key]


@tool
def execute_athena_query(input: str) -> str:
    """Executes an Athena SQL query and returns up to 10 rows. Returns error info if the query fails."""
    import re

    # Add basic error handling for common mistakes
    if "DATE_FORMAT" in input:
        return f"ERROR: DATE_FORMAT is not supported in Trino. Use format_datetime(from_unixtime(...), 'format') instead.\nQuery:\n{input}"
    if "unix_timestamp" in input.lower():
        return f"ERROR: unix_timestamp is not supported in Trino. Use from_unixtime(...) instead.\nQuery:\n{input}"
    if 'LIKE "' in input:
        return f"ERROR: Use single quotes for string literals in LIKE clauses. Double quotes are for identifiers only.\nQuery:\n{input}"  # Check for common column name mistakes in WHERE/FROM/JOIN clauses (not SELECT aliases)
    common_mistakes = [
        ("s.date", "s.created_at or w.start_time"),
        ("e.name", "e.title"),
        ("exercises.name", "exercises.title"),
        ("sets.date", "sets.created_at or workouts.start_time"),
        ("exercise_name", "title"),
    ]

    # Only check mistakes in WHERE/FROM/JOIN clauses, not in SELECT aliases
    lines = input.split("\n")
    for line in lines:
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in ["where", "from", "join", "on"]):
            for mistake, correction in common_mistakes:
                if mistake in line:
                    return f"ERROR: Column '{mistake}' does not exist. Use '{correction}' instead.\nQuery:\n{input}"

    # Check for aliases being used in GROUP BY or ORDER BY clauses
    group_by_alias_pattern = (
        r"GROUP\s+BY\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*"
    )
    order_by_alias_pattern = r"ORDER\s+BY\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s+(?:ASC|DESC))?(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*(?:\s+(?:ASC|DESC))?)*"

    if re.search(group_by_alias_pattern, input, re.IGNORECASE):
        return f"ERROR: Cannot use column aliases in GROUP BY clause. Use the full expression instead.\nExample: GROUP BY DATE(FROM_UNIXTIME(CAST(w.start_time AS DOUBLE)))\nQuery:\n{input}"

    if re.search(order_by_alias_pattern, input, re.IGNORECASE):
        # Check if it's actually an alias (simple identifier) vs a function/expression
        order_by_match = re.search(
            r"ORDER\s+BY\s+([a-zA-Z_][a-zA-Z0-9_]*)", input, re.IGNORECASE
        )
        if order_by_match:
            order_by_field = order_by_match.group(1)
            # If it doesn't contain parentheses or dots, it's likely an alias
            if "(" not in order_by_field and "." not in order_by_field:
                return f"ERROR: Cannot use column alias '{order_by_field}' in ORDER BY clause. Use the full expression instead.\nExample: ORDER BY SUM(s.weight_kg * s.reps) DESC\nQuery:\n{input}"

    # Check for any string equality comparisons - always enforce LIKE for strings
    # Look for patterns like column_name = 'value' for string columns (but not numeric comparisons)
    string_equality_pattern = r"[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*'[^']*'"
    if re.search(string_equality_pattern, input):
        matches = re.findall(string_equality_pattern, input)
        return f"ERROR: Always use LIKE with wildcards for string matching, never use exact equality (=). Found: {matches}\nExample: WHERE LOWER(title) LIKE LOWER('%Squat%') AND LOWER(equipment_category) LIKE LOWER('%barbell%')\nQuery:\n{input}"

    payload = {"query": input}
    response = lambda_client.invoke(
        FunctionName="ExecuteAthenaQuery",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    raw_body = response["Payload"].read().decode("utf-8").strip()

    if not raw_body:
        return f"ERROR: Empty response from Lambda for query:\n{input}"

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as e:
        return f"ERROR: Failed to parse Lambda response. Raw body:\n{raw_body}"

    body = parsed.get("body")
    if body is None:
        return f"ERROR: Athena query failed or returned no response.\nQuery:\n{input}\nRaw Lambda response:\n{raw_body}"
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return f"ERROR: Failed to parse 'body' as JSON: {body}"

    if not isinstance(body, dict) or "rows" not in body:
        return f"ERROR: Athena query failed or returned no rows.\nQuery:\n{input}\nError:\n{body}"

    rows = body["rows"]
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])  # skip headers
    return f"Results for query:\n{input}\n\n{formatted_rows}"


tools = [get_glue_table_schema, execute_athena_query]


# Define the state for the agent
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Create the LLM with tools
llm_with_tools = llm.bind_tools(tools)


# Define the agent node
def agent_node(state: State):
    """The main agent node that processes messages and decides on actions"""
    system_message = SystemMessage(
        content="""
You are a data assistant specialized in analyzing AWS Glue tables via Athena using Trino SQL syntax.

CRITICAL: You have access to TWO tools:
- get_glue_table_schema: retrieves schemas for workouts, exercises, and sets tables
- execute_athena_query: runs SQL queries against the Athena database

ALWAYS start by calling get_glue_table_schema first to get the exact table and column names.

FORBIDDEN FUNCTIONS (Will cause query failure):
- DATE_FORMAT(...) (MySQL function, NOT Trino)
- unix_timestamp(...)
- DATE_TRUNC(...) for timestamp comparisons

REQUIRED Trino Functions for Timestamps:
- from_unixtime(bigint_column) - converts UNIX timestamp to timestamp
- format_datetime(from_unixtime(column), '%H:%i') - for HH:MM format
- hour(from_unixtime(column)) - extract hour
- minute(from_unixtime(column)) - extract minute
- year(from_unixtime(column)) - extract year

Rules:
1. ALWAYS call get_glue_table_schema first to get exact table names
2. CRITICAL: Use ONLY columns that exist in the schema - NEVER guess or assume column names
3. CRITICAL: If a column name doesn't appear in the schema, it DOES NOT EXIST
4. Use comments from the schema to understand column types and meanings.
5. For BIGINT UNIX timestamps, wrap in from_unixtime(...)
6. For date filtering: date(from_unixtime(column)) >= date('YYYY-MM-DD')
7. For time formatting: format_datetime(from_unixtime(column), '%H:%i')
8. CRITICAL: NEVER use column aliases in GROUP BY or ORDER BY - ALWAYS use full expressions
   - WRONG: GROUP BY workout_date, ORDER BY total_volume  
   - CORRECT: GROUP BY DATE(FROM_UNIXTIME(CAST(w.start_time AS DOUBLE))), ORDER BY SUM(s.weight_kg * s.reps) DESC
9. If query fails, read error and fix syntax issues
10. MANDATORY: Always use LOWER() for case-insensitive string comparisons
11. MANDATORY: NEVER use exact equality (=) for ANY string values - ALWAYS use LIKE with wildcards
12. MANDATORY: String matching format: WHERE LOWER(column) LIKE LOWER('%search_term%')
13. REASON: Exercise names, equipment categories, and other strings can have slight variations
14. NEVER use ESCAPE clause - it's not supported in Trino. Use LIKE with proper wildcards or regexp_like() for complex patterns
15. ALWAYS use single quotes for string literals, NEVER double quotes. Double quotes are for identifiers only.
17. As a response return the query result in a human-readable format, not JSON or code blocks.

CORRECT EXAMPLES:
- WHERE LOWER(e.title) LIKE LOWER('%Squat%') AND LOWER(e.equipment_category) LIKE LOWER('%barbell%')
- WHERE LOWER(e.muscle_group) LIKE LOWER('%chest%')

INCORRECT EXAMPLES:
- WHERE e.title = 'Squat' (exact match, case-sensitive)
- WHERE e.equipment_category = 'barbell' (exact match, case-sensitive)
- WHERE LOWER(e.title) = LOWER('Squat') (exact match, even if case-insensitive)
"""
    )

    messages = [system_message] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Create the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))

# Add edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END,
    },
)
workflow.add_edge("tools", "agent")

# Compile the graph
graph = workflow.compile()


# Function to run the agent
def run_agent(query: str):
    """Run the LangGraph agent with the given query"""
    print(f"Processing query: {query}")

    result = graph.invoke({"messages": [HumanMessage(content=query)]})

    return result["messages"][-1].content


# Run the agent
response = run_agent(
    "in what exercise I had the largest volume (the weight lifted in all exercises in a single workout) in my workouts? give me the day, the exercise name, and the volume in a human-readable format, not JSON or code blocks."
)

print("Final Response:")
print(response)

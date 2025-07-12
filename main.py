import boto3
import json
import logging
from langchain_core.tools import tool
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Annotated, TypedDict

# Configure logging to show detailed agent interactions
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


region = "eu-central-1"
bedrock_client = boto3.client("bedrock-runtime", region_name=region)

# Claude 3 via Bedrock with low temperature for analytical precision
llm = ChatBedrock(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    region=region,
    model_kwargs={
        "temperature": 1,  # Low temperature for more deterministic, focused responses
        "max_tokens": 4096,  # Sufficient tokens for complex SQL queries and explanations
    },
)

lambda_client = boto3.client("lambda", region_name=region)

# Cache for tool results to avoid repeated calls
_tool_cache = {}


@tool
def get_glue_table_schema(input: str) -> str:
    """Return schemas for workouts, exercises, and sets tables: table name, column names, types, and comments."""
    print("🔍 TOOL CALL: get_glue_table_schema")
    print(f"📥 Input: {input}")

    cache_key = "glue_schema"
    if cache_key in _tool_cache:
        print("💾 Using cached schema result")
        return _tool_cache[cache_key]

    print("🌐 Calling Lambda function: GetGlueTableSchema")
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

    final_result = "\n\n".join(result)
    _tool_cache[cache_key] = final_result

    print("✅ Schema retrieved successfully")
    print(
        f"📊 Found {len(result)} tables: {', '.join([label for label in ['workouts', 'exercises', 'sets']])}"
    )

    return final_result


@tool
def execute_athena_query(input: str) -> str:
    """Executes an Athena SQL query and returns up to 10 rows. Returns error info if the query fails."""
    print("🔍 TOOL CALL: execute_athena_query")
    print(f"📥 SQL Query:\n{input}")

    import re

    # Add basic error handling for common mistakes
    if "DATE_FORMAT" in input:
        error_msg = f"ERROR: DATE_FORMAT is not supported in Trino. Use format_datetime(from_unixtime(...), 'format') instead.\nQuery:\n{input}"
        print(f"❌ Validation Error: {error_msg}")
        return error_msg
    if "unix_timestamp" in input.lower():
        error_msg = f"ERROR: unix_timestamp is not supported in Trino. Use from_unixtime(...) instead.\nQuery:\n{input}"
        print(f"❌ Validation Error: {error_msg}")
        return error_msg
    if 'LIKE "' in input:
        error_msg = f"ERROR: Use single quotes for string literals in LIKE clauses. Double quotes are for identifiers only.\nQuery:\n{input}"
        print(f"❌ Validation Error: {error_msg}")
        return error_msg

    # Check for common column name mistakes in WHERE/FROM/JOIN clauses (not SELECT aliases)
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
                    error_msg = f"ERROR: Column '{mistake}' does not exist. Use '{correction}' instead.\nQuery:\n{input}"
                    print(f"❌ Column Error: {error_msg}")
                    return error_msg

    # Check for aliases being used in GROUP BY or ORDER BY clauses
    group_by_alias_pattern = (
        r"GROUP\s+BY\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*"
    )
    order_by_alias_pattern = r"ORDER\s+BY\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\s+(?:ASC|DESC))?(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*(?:\s+(?:ASC|DESC))?)*"

    if re.search(group_by_alias_pattern, input, re.IGNORECASE):
        error_msg = f"ERROR: Cannot use column aliases in GROUP BY clause. Use the full expression instead.\nExample: GROUP BY DATE(FROM_UNIXTIME(CAST(w.start_time AS DOUBLE)))\nQuery:\n{input}"
        print(f"❌ GROUP BY Error: {error_msg}")
        return error_msg

    if re.search(order_by_alias_pattern, input, re.IGNORECASE):
        # Check if it's actually an alias (simple identifier) vs a function/expression
        order_by_match = re.search(
            r"ORDER\s+BY\s+([a-zA-Z_][a-zA-Z0-9_]*)", input, re.IGNORECASE
        )
        if order_by_match:
            order_by_field = order_by_match.group(1)
            # If it doesn't contain parentheses or dots, it's likely an alias
            if "(" not in order_by_field and "." not in order_by_field:
                error_msg = f"ERROR: Cannot use column alias '{order_by_field}' in ORDER BY clause. Use the full expression instead.\nExample: ORDER BY SUM(s.weight_kg * s.reps) DESC\nQuery:\n{input}"
                print(f"❌ ORDER BY Error: {error_msg}")
                return error_msg

    # Check for any string equality comparisons - always enforce LIKE for strings
    # Look for patterns like column_name = 'value' for string columns (but not numeric comparisons)
    string_equality_pattern = r"[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*'[^']*'"
    if re.search(string_equality_pattern, input):
        matches = re.findall(string_equality_pattern, input)
        error_msg = f"ERROR: Always use LIKE with wildcards for string matching, never use exact equality (=). Found: {matches}\nExample: WHERE LOWER(title) LIKE LOWER('%Squat%') AND LOWER(equipment_category) LIKE LOWER('%barbell%')\nQuery:\n{input}"
        print(f"❌ String Equality Error: {error_msg}")
        return error_msg

    print("✅ Query validation passed")
    print("🌐 Executing query via Lambda function: ExecuteAthenaQuery")

    payload = {"query": input}
    response = lambda_client.invoke(
        FunctionName="ExecuteAthenaQuery",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    raw_body = response["Payload"].read().decode("utf-8").strip()

    if not raw_body:
        error_msg = f"ERROR: Empty response from Lambda for query:\n{input}"
        print(f"❌ Lambda Error: {error_msg}")
        return error_msg

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as e:
        error_msg = f"ERROR: Failed to parse Lambda response. Raw body:\n{raw_body}"
        print(f"❌ Parse Error: {error_msg}")
        return error_msg

    body = parsed.get("body")
    if body is None:
        error_msg = f"ERROR: Athena query failed or returned no response.\nQuery:\n{input}\nRaw Lambda response:\n{raw_body}"
        print(f"❌ Athena Error: {error_msg}")
        return error_msg
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            error_msg = f"ERROR: Failed to parse 'body' as JSON: {body}"
            print(f"❌ Body Parse Error: {error_msg}")
            return error_msg

    if not isinstance(body, dict) or "rows" not in body:
        error_msg = f"ERROR: Athena query failed or returned no rows.\nQuery:\n{input}\nError:\n{body}"
        print(f"❌ Query Result Error: {error_msg}")
        return error_msg

    rows = body["rows"]
    formatted_rows = "\n".join(", ".join(row) for row in rows[1:])  # skip headers
    result = f"Results for query:\n{input}\n\n{formatted_rows}"

    print(f"✅ Query executed successfully")
    print(f"📊 Retrieved {len(rows)-1} rows of data")

    return result


tools = [get_glue_table_schema, execute_athena_query]


# Define the state for the agent
class State(TypedDict):
    messages: Annotated[list, add_messages]


# Create the LLM with tools
llm_with_tools = llm.bind_tools(tools)


# Define the agent node
def agent_node(state: State):
    """The main agent node that processes messages and decides on actions"""
    print("\n" + "=" * 60)
    print("🤖 AGENT REASONING PHASE")
    print("=" * 60)

    # Show current message count and recent messages
    message_count = len(state["messages"])
    print(f"📝 Processing message {message_count} in conversation")

    # Show the last user message or system message
    if state["messages"]:
        last_message = state["messages"][-1]
        message_type = type(last_message).__name__
        print(f"📩 Last message type: {message_type}")
        if hasattr(last_message, "content"):
            content_preview = (
                last_message.content[:200] + "..."
                if len(last_message.content) > 200
                else last_message.content
            )
            print(f"📄 Content preview: {content_preview}")

    system_message = SystemMessage(
        content="""

# Data Assistant System Prompt for Claude + AWS Glue + Athena (Trino SQL)

You are a data assistant specialized in analyzing AWS Glue tables via Athena using Trino SQL syntax.

CRITICAL: You have access to TWO tools:
- `get_glue_table_schema`: retrieves schemas for workouts, exercises, and sets tables
- `execute_athena_query`: runs SQL queries against the Athena database

ALWAYS call `get_glue_table_schema` FIRST to get the exact table names and columns before writing any queries.

---

## SQL Rules & Behavior

1. Use only columns and tables returned by `get_glue_table_schema`
   Never guess or assume column names.
   If a column doesn't appear in the schema, it DOES NOT exist.

2. Use table comments to understand column meanings.

---

## GROUP BY / ORDER BY
NEVER use column aliases in GROUP BY or ORDER BY — use the full expression or positional indexes (e.g., ORDER BY 2)
Correct: GROUP BY date(from_unixtime(w.start_time))
Correct: ORDER BY SUM(s.weight_kg * s.reps) DESC 

Wrong: GROUP BY workout_date
Wrong: ORDER BY total_volume
---


## Timestamp Handling (UNIX BIGINT columns)

Allowed:
- `from_unixtime(start_time)`
- `date(from_unixtime(end_time)) >= date('YYYY-MM-DD')`
- `hour(from_unixtime(...))`, `minute(...)`, `year(...)`
- `format_datetime(from_unixtime(...), '%H:%i')`

Forbidden (will FAIL in Trino):
- `unix_timestamp(...)`
- `DATE_FORMAT(...)` (MySQL)
- `DATE_TRUNC(...)` for filtering

Example (correct):
```
WHERE date(from_unixtime(w.start_time)) >= date('2024-01-01')
```

Example (wrong):
```
WHERE w.start_time >= '2024-01-01'
```

---

## String Matching

Always use:
```
WHERE LOWER(e.title) LIKE LOWER('%squat%')
```

Never use:
- `e.title = 'Squat'` (case-sensitive, exact)
- `LOWER(e.title) = LOWER('Squat')` (still exact match)

Never use the ESCAPE clause — it is not supported in Trino.

---

## Additional Rules

- Use single quotes 'value' for strings
- Do not use double quotes for string literals
- If a query fails, fix based on the error (e.g., column not found, wrong type) and retry
- Use concise, readable plain-text for results (not JSON or code blocks)
- Treat “I”, “my”, “me” as the user’s data

---



```
SELECT w.name, date(from_unixtime(w.start_time)) AS workout_date
FROM workouts_...
WHERE date(from_unixtime(w.start_time)) >= date('2024-01-01')
ORDER BY date(from_unixtime(w.start_time)) DESC
```

```
SELECT e.title, s.reps, s.weight_kg
FROM exercises_... e
JOIN sets_... s ON e.id = s.exercise_id
WHERE LOWER(e.muscle_group) LIKE LOWER('%chest%')
```

---

## ERROR HANDLING

If you receive an error message about your previous query, **read the error carefully**.

- Extract the exact cause (e.g., "Cannot use column aliases in GROUP BY").
- Rewrite your query **to fix the specific error**.
- Explain what you fixed and why.
- Then provide only the corrected SQL query (no JSON, no code blocks).
- Do not repeat the same error.

Example error:
ERROR: Cannot use column aliases in GROUP BY clause. Use the full expression instead.

Correction:
I replaced the alias in GROUP BY with the full expression as required.

New query:
SELECT date(from_unixtime(w.start_time)) AS workout_date, ...
GROUP BY date(from_unixtime(w.start_time)), ...
---

You must strictly follow all rules above. Queries that violate these rules will fail.

"""
    )

    messages = [system_message] + state["messages"]
    print(f"🧠 Sending {len(messages)} messages to LLM for reasoning...")

    print("\n🔄 CALLING BEDROCK LLM...")
    response = llm_with_tools.invoke(messages)

    print("✅ LLM Response received")
    print(f"📄 Response type: {type(response).__name__}")

    # Check if the response contains tool calls
    if (
        hasattr(response, "additional_kwargs")
        and "tool_calls" in response.additional_kwargs
    ):
        tool_calls = response.additional_kwargs["tool_calls"]
        if tool_calls:
            print(f"🔧 Agent wants to use {len(tool_calls)} tools:")
            for i, tool_call in enumerate(tool_calls, 1):
                tool_name = tool_call.get("function", {}).get("name", "Unknown tool")
                print(f"  {i}. {tool_name}")
    elif hasattr(response, "content") and response.content:
        print("💬 Agent provided direct response (no tool calls)")
        content_str = str(response.content)
        content_preview = (
            content_str[:100] + "..." if len(content_str) > 100 else content_str
        )
        print(f"📝 Content preview: {content_preview}")

    print("=" * 60)

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
    print("\n" + "=" * 80)
    print("🚀 STARTING AGENT EXECUTION")
    print("=" * 80)
    print(f"📝 User Query: {query}")
    print("=" * 80)

    # Stream the graph execution to see each step
    events = []
    initial_state: State = {"messages": [HumanMessage(content=query)]}

    print("\n🔄 AGENT WORKFLOW EXECUTION:")
    print("-" * 50)

    step_count = 0
    try:
        for event in graph.stream(initial_state):
            step_count += 1
            print(f"\n📍 STEP {step_count}: {list(event.keys())}")

            # Store event for analysis
            events.append(event)

            # Update state
            for node_name, node_output in event.items():
                if node_output and "messages" in node_output:
                    print(
                        f"   🔄 Node '{node_name}' produced {len(node_output['messages'])} messages"
                    )

                    # Show the latest message content if it's not a tool call
                    if node_output["messages"]:
                        latest_msg = node_output["messages"][-1]
                        if hasattr(latest_msg, "content") and latest_msg.content:
                            msg_content = str(latest_msg.content)
                            if not (
                                hasattr(latest_msg, "additional_kwargs")
                                and "tool_calls" in latest_msg.additional_kwargs
                            ):
                                content_preview = (
                                    msg_content[:150] + "..."
                                    if len(msg_content) > 150
                                    else msg_content
                                )
                                print(f"   💬 Message content: {content_preview}")

        print("\n" + "=" * 80)
        print("✅ AGENT EXECUTION COMPLETED")
        print("=" * 80)

        # Get the final result by running the full graph
        final_result = graph.invoke(initial_state)
        final_content = final_result["messages"][-1].content

        print(f"📊 Total steps executed: {step_count}")
        print(f"📝 Final message count: {len(final_result['messages'])}")

        return final_content

    except Exception as e:
        print(f"\n❌ ERROR during agent execution: {str(e)}")
        print("=" * 80)
        raise


# Run the agent
response = run_agent(
    "in what exercise I had the largest volume (the weight lifted in all exercises in a single workout) in my workouts? give me the day, the exercise name, and the volume in a human-readable format, not JSON or code blocks."
)

print("Final Response:")
print(response)

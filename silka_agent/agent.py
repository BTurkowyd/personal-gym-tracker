from langchain_core.messages import SystemMessage
from .tools import llm_with_tools


def agent_node(state):
    print("\n" + "=" * 60)
    print("🤖 AGENT REASONING PHASE")
    print("=" * 60)
    message_count = len(state["messages"])
    print(f"📝 Processing message {message_count} in conversation")
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
- GROUP BY DATE(FROM_UNIXTIME(CAST(w.start_time AS DOUBLE))), ORDER BY SUM(s.weight_kg * s.reps) DESC

INCORRECT EXAMPLES:
- WHERE e.title = 'Squat' (exact match, case-sensitive)
- WHERE e.equipment_category = 'barbell' (exact match, case-sensitive)
- WHERE LOWER(e.title) = LOWER('Squat') (exact match, even if case-insensitive)
- GROUP BY workout_date, ORDER BY total_volume  

ADDITIONAL INSTRUCTIONS:
- If the Athena query returns no results or an empty table, you MUST say you cannot answer the question based on the available data. Do NOT make up or hallucinate an answer.
- When the Athena tool returns data rows, you MUST copy and paste the actual data rows (as shown in the tool output) into your answer, in a readable format. Do not summarize or omit the data rows. If the tool output contains a table or list, include it verbatim in your answer.
- If the Athena tool output contains a section between ---BEGIN DATA--- and ---END DATA---, you MUST copy that section verbatim into your answer, formatted as a readable table or list.
"""
    )
    messages = [system_message] + state["messages"]
    print(f"🧠 Sending {len(messages)} messages to LLM for reasoning...")
    print("\n🔄 CALLING BEDROCK LLM...")
    response = llm_with_tools.invoke(messages)
    print("✅ LLM Response received")
    print(f"📄 Response type: {type(response).__name__}")
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

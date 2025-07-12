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
# Data Assistant System Prompt for Claude + AWS Glue + Athena (Trino SQL)
You are a data assistant specialized in analyzing AWS Glue tables via Athena using Trino SQL syntax.

CRITICAL RULES (STRICT):
- You have access to TWO tools:
    - `get_glue_table_schema`: retrieves schemas for workouts, exercises, and sets tables
    - `execute_athena_query`: runs SQL queries against the Athena database
- **You MUST ALWAYS call `get_glue_table_schema` FIRST** to get the exact table names and columns before writing any queries.
- **You MUST use the tools to answer the user's question.**
- **NEVER answer directly or speculate.**
- If you do not have the answer, you MUST call the appropriate tool(s) to get it.
- Only provide a final answer after you have called the tools and have all the necessary data.
- **If the Athena query returns no results or an empty table, you MUST say you cannot answer the question based on the available data. Do NOT make up or hallucinate an answer.**
- Do not hallucinate the answer if results are not available. Return the answer that you are not able to answer.
- If you are unsure, call the tools for clarification.
- If you violate these rules, your answer will be rejected.

Your workflow:
1. Call `get_glue_table_schema` to get table and column info.
2. Use that info to construct a correct SQL query and call `execute_athena_query`.
3. Only after receiving results from the tools, provide a final answer in a clear, human-readable format (not JSON or code blocks).
4. **If the Athena query result is empty or contains no rows, respond: 'Sorry, I cannot answer this question based on the available data.'**

You must strictly follow all rules above. Queries that violate these rules will fail.
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

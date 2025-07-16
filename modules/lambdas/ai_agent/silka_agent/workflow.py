from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_aws import ChatBedrock
from typing import Annotated, TypedDict
from .tools import tools
from .agent import agent_node
from .config import region, model_name, model_kwargs
from langchain_core.messages import HumanMessage

llm = ChatBedrock(model=model_name, region=region, model_kwargs=model_kwargs)
llm_with_tools = llm.bind_tools(tools)


class State(TypedDict):
    messages: Annotated[list, add_messages]


# Build the workflow graph
workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(tools))
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
graph = workflow.compile()


def run_agent(query: str):
    print("\n" + "=" * 80)
    print("🚀 STARTING AGENT EXECUTION")
    print("=" * 80)
    print(f"📝 User Query: {query}")
    print("=" * 80)
    events = []
    initial_state: State = {"messages": [HumanMessage(content=query)]}
    print("\n🔄 AGENT WORKFLOW EXECUTION:")
    print("-" * 50)
    step_count = 0
    try:
        last_message = None
        for event in graph.stream(initial_state):
            step_count += 1
            print(f"\n📍 STEP {step_count}: {list(event.keys())}")
            events.append(event)
            for node_name, node_output in event.items():
                if node_output and "messages" in node_output:
                    print(
                        f"   🔄 Node '{node_name}' produced {len(node_output['messages'])} messages"
                    )
                    if node_output["messages"]:
                        latest_msg = node_output["messages"][-1]
                        last_message = latest_msg
                        if hasattr(latest_msg, "content") and latest_msg.content:
                            msg_content = str(latest_msg.content)
                            if not (
                                hasattr(latest_msg, "additional_kwargs")
                                and "tool_calls" in latest_msg.additional_kwargs
                            ):
                                print(f"   💬 Message content: {msg_content}")
        print("\n" + "=" * 80)
        print("✅ AGENT EXECUTION COMPLETED")
        print("=" * 80)
        print(f"📊 Total steps executed: {step_count}")
        print(
            f"📝 Final message count: {len(events[-1][list(events[-1].keys())[0]]['messages']) if events else 0}"
        )
        if last_message and hasattr(last_message, "content"):
            return last_message.content
        return None
    except Exception as e:
        print(f"\n❌ ERROR during agent execution: {str(e)}")
        print("=" * 80)
        raise

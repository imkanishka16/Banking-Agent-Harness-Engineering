from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt

from app.agents.harnessed.prompts import harnessed_system_prompt
from app.agents.harnessed.state import AgentState
from app.config import get_settings
from app.harness.approval import APPROVAL_REQUIRED_TOOLS, build_approval_request
from app.harness.budget import BUDGET_MESSAGE, budget_exceeded
from app.tools.session_tools import Session, build_session_tools


def build_harnessed_agent(session: Session, checkpointer=None):
    settings = get_settings()
    tools = build_session_tools(session)
    llm = ChatOpenAI(
        model=settings.openai_model, api_key=settings.openai_api_key, temperature=0
    ).bind_tools(tools, parallel_tool_calls=False)  # one action at a time
    system = SystemMessage(harnessed_system_prompt(session))

    # ---------- nodes ----------

    def agent(state: AgentState) -> dict:
        response = llm.invoke([system, *state["messages"]])
        return {"messages": [response], "steps": state.get("steps", 0) + 1}

    def approval(state: AgentState) -> Command[Literal["tools", "agent"]]:
        call = state["messages"][-1].tool_calls[0]
        request = build_approval_request(session.account_id, call)
        if request is None:
            # Policy will block it inside the tool and return the reason
            return Command(goto="tools")

        # Pauses the graph. On resume, this node re-runs from the top, so
        # everything above this line must be read-only (it is).
        decision = interrupt(request)

        if decision.get("approved"):
            return Command(goto="tools")
        return Command(
            goto="agent",
            update={"messages": [ToolMessage(
                content='{"declined_by_customer": true}', tool_call_id=call["id"]
            )]},
        )

    def budget_stop(state: AgentState) -> dict:
        call = state["messages"][-1].tool_calls[0]
        return {"messages": [
            # Every tool call needs a reply, or the next OpenAI request fails
            ToolMessage(content='{"error": "Not executed: step budget exceeded"}',
                        tool_call_id=call["id"]),
            AIMessage(content=BUDGET_MESSAGE),
        ]}

    # ---------- routing ----------

    def route_after_agent(state: AgentState) -> str:
        last = state["messages"][-1]
        if not last.tool_calls:
            return END
        if budget_exceeded(state["steps"]):
            return "budget_exceeded"
        if last.tool_calls[0]["name"] in APPROVAL_REQUIRED_TOOLS:
            return "approval"
        return "tools"

    # ---------- wiring ----------

    builder = StateGraph(AgentState)
    builder.add_node("agent", agent)
    builder.add_node("approval", approval)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("budget_exceeded", budget_stop)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent", route_after_agent, ["tools", "approval", "budget_exceeded", END]
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("budget_exceeded", END)

    return builder.compile(checkpointer=checkpointer or InMemorySaver())
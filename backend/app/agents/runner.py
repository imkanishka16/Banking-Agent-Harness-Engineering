"""Runs either agent for one turn and records the trace."""
from functools import lru_cache

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.agents.harnessed.graph import build_harnessed_agent
from app.agents.naive_agent import build_naive_agent
from app.harness.tracer import tracer
from app.tools.session_tools import Session

# Demo: one logged-in customer. A real app would take this from auth.
DEMO_SESSION = Session(account_id="ACC-1001", customer_name="Demo Customer")


class NoPendingApproval(Exception):
    pass


@lru_cache
def _agent(mode: str):
    if mode == "naive":
        return build_naive_agent(checkpointer=InMemorySaver())
    return build_harnessed_agent(DEMO_SESSION)


def reset_agents() -> None:
    _agent.cache_clear()  # fresh agents = fresh conversation memory


def _config(mode: str, thread_id: str) -> dict:
    return {"configurable": {"thread_id": f"{mode}:{thread_id}"}}


def _run(mode: str, thread_id: str, payload) -> dict:
    agent = _agent(mode)
    config = _config(mode, thread_id)
    before = len(agent.get_state(config).values.get("messages", []))

    result = agent.invoke(payload, config)

    new_messages = result["messages"][before:]
    events = tracer.record_messages(thread_id, mode, new_messages)

    approval = None
    if "__interrupt__" in result:
        approval = result["__interrupt__"][0].value
        events.append(tracer.record(thread_id, mode, "approval_requested", approval))

    reply = next(
        (m.content for m in reversed(new_messages)
         if isinstance(m, AIMessage) and m.content and not m.tool_calls),
        None,
    )
    return {
        "thread_id": thread_id,
        "mode": mode,
        "status": "awaiting_approval" if approval else "completed",
        "reply": reply,
        "approval": approval,
        "events": events,
    }


def chat(mode: str, thread_id: str, message: str) -> dict:
    payload = {"messages": [{"role": "user", "content": message}]}
    if mode == "harnessed":
        payload["steps"] = 0  # reset the budget each turn
    return _run(mode, thread_id, payload)


def approve(thread_id: str, approved: bool) -> dict:
    agent = _agent("harnessed")
    if not agent.get_state(_config("harnessed", thread_id)).next:
        raise NoPendingApproval(f"No transfer is waiting for approval in thread {thread_id}")

    decision = tracer.record(thread_id, "harnessed", "approval_decision", {"approved": approved})
    out = _run("harnessed", thread_id, Command(resume={"approved": approved}))
    out["events"].insert(0, decision)
    return out
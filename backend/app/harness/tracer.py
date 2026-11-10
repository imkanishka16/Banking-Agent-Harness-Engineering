"""Audit trail: every harness decision becomes a structured, timestamped event."""
import json
import threading
from collections import defaultdict
from datetime import datetime, timezone

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


def _parse(content):
    if not isinstance(content, str):
        return content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw": content}


def classify(message) -> list[tuple[str, dict]]:
    """Turn one message into zero or more (event_type, data) pairs."""
    if isinstance(message, HumanMessage):
        return [("user_message", {"content": message.content})]

    if isinstance(message, AIMessage):
        events = [("tool_call", {"name": tc["name"], "args": tc["args"]})
                  for tc in message.tool_calls]
        if message.content:
            events.append(("agent_reply", {"content": message.content}))
        return events

    if isinstance(message, ToolMessage):
        result = _parse(message.content)
        if not isinstance(result, dict):
            return [("tool_result", {"tool": message.name, "result": result})]
        if "blocked_by_policy" in result:
            return [("policy_block", {"tool": message.name,
                                      "code": result["blocked_by_policy"],
                                      "reason": result.get("reason")})]
        if result.get("declined_by_customer"):
            return [("transfer_declined", {})]
        if "budget" in str(result.get("error", "")):
            return [("budget_exceeded", {})]
        events = []
        if "security_notice" in result:
            events.append(("guard_finding", {"tool": message.name,
                                             "notice": result["security_notice"]}))
        events.append(("tool_result", {"tool": message.name, "result": result}))
        return events

    return []


class Tracer:
    def __init__(self) -> None:
        self._events: dict[str, list[dict]] = defaultdict(list)
        self._lock = threading.Lock()

    def record(self, thread_id: str, mode: str, event_type: str, data: dict | None = None) -> dict:
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "thread_id": thread_id,
            "mode": mode,
            "type": event_type,
            "data": data or {},
        }
        with self._lock:
            self._events[thread_id].append(event)
        return event

    def record_messages(self, thread_id: str, mode: str, messages: list) -> list[dict]:
        return [self.record(thread_id, mode, t, d)
                for m in messages for t, d in classify(m)]

    def get(self, thread_id: str) -> list[dict]:
        with self._lock:
            return list(self._events.get(thread_id, []))

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


tracer = Tracer()
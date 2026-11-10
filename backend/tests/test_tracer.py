from langchain_core.messages import ToolMessage

from app.harness.tracer import classify


def _types(message):
    return [t for t, _ in classify(message)]


def test_policy_block_is_recorded():
    m = ToolMessage(content='{"blocked_by_policy": "LIMIT_EXCEEDED", "reason": "too much"}',
                    tool_call_id="1", name="transfer_money")
    assert _types(m) == ["policy_block"]


def test_guard_finding_is_recorded():
    m = ToolMessage(content='{"count": 1, "beneficiaries": [], "security_notice": "removed"}',
                    tool_call_id="2", name="find_beneficiaries")
    assert _types(m) == ["guard_finding", "tool_result"]
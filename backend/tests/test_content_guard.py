from app.bank.mock_bank import bank
from app.harness.content_guard import REMOVED, scan


def test_detects_injection_in_beneficiary_nickname():
    assert scan(bank.beneficiaries["BEN-04"].nickname)


def test_normal_text_is_not_flagged():
    for text in ["Brother", "Gym trainer", "Rent", "Nimal Perera", "Monthly rent payment"]:
        assert scan(text) == [], text


def test_tool_output_is_sanitized_before_llm_sees_it(tools):
    result = tools["find_beneficiaries"].invoke({})
    ben4 = next(b for b in result["beneficiaries"] if b["beneficiary_id"] == "BEN-04")
    assert ben4["nickname"] == REMOVED
    assert "security_notice" in result
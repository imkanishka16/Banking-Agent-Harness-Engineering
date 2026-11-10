import pytest

from app.bank.mock_bank import bank
from app.harness.tool_policy import check_transfer

# Fixtures (fresh_bank, tools) live in conftest.py


# ---- policy rules ----

def test_allows_valid_transfer():
    assert check_transfer("ACC-1001", "BEN-01", 5_000).allowed


def test_blocks_other_customers_beneficiary():
    d = check_transfer("ACC-1001", "BEN-99", 100)
    assert not d.allowed and d.code == "UNKNOWN_BENEFICIARY"


def test_blocks_over_limit():
    d = check_transfer("ACC-1001", "BEN-01", 60_000)
    assert not d.allowed and d.code == "LIMIT_EXCEEDED"


def test_blocks_insufficient_funds():
    bank.accounts["ACC-1001"].balance = 1_000
    d = check_transfer("ACC-1001", "BEN-01", 5_000)
    assert not d.allowed and d.code == "INSUFFICIENT_FUNDS"


@pytest.mark.parametrize("amount", [0, -500])
def test_blocks_non_positive_amount(amount):
    assert check_transfer("ACC-1001", "BEN-01", amount).code == "INVALID_AMOUNT"


def test_blocks_when_daily_limit_reached():
    bank.transfer("ACC-1001", "BEN-01", 50_000)
    bank.transfer("ACC-1001", "BEN-02", 50_000)
    d = check_transfer("ACC-1001", "BEN-03", 10_000)
    assert not d.allowed and d.code == "DAILY_LIMIT_EXCEEDED"


# ---- session binding ----

def test_llm_cannot_choose_account(tools):
    for t in tools.values():
        assert "account_id" not in t.args, f"{t.name} exposes account_id to the LLM"


def test_blocked_transfer_does_not_move_money(tools):
    result = tools["transfer_money"].invoke({"beneficiary_id": "BEN-99", "amount": 50_000})
    assert result["blocked_by_policy"] == "UNKNOWN_BENEFICIARY"
    assert bank.get_account("ACC-1001").balance == 120_000


def test_cannot_read_other_customers_transaction(tools):
    tx = bank.transfer("ACC-2002", "BEN-99", 10)
    assert tools["get_transaction_status"].invoke({"transaction_id": tx.transaction_id}) == {
        "error": "Transaction not found."
    }


def test_splitting_cannot_bypass_daily_limit(tools):
    """Attack 7: three transfers that each pass the per-transfer limit."""
    results = [
        tools["transfer_money"].invoke({"beneficiary_id": "BEN-01", "amount": 40_000})
        for _ in range(3)
    ]
    assert "transaction_id" in results[0]
    assert "transaction_id" in results[1]
    assert results[2]["blocked_by_policy"] == "DAILY_LIMIT_EXCEEDED"
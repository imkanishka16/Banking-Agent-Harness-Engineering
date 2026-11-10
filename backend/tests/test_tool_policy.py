import pytest

from app.bank.mock_bank import bank
from app.harness.tool_policy import check_transfer
from app.tools.session_tools import Session, build_session_tools


@pytest.fixture(autouse=True)
def fresh_bank():
    bank.reset()


@pytest.fixture
def tools():
    t = build_session_tools(Session(account_id="ACC-1001", customer_name="Demo Customer"))
    return {tool.name: tool for tool in t}


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
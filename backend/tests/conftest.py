import pytest

from app.bank.mock_bank import bank
from app.tools.session_tools import Session, build_session_tools


@pytest.fixture(autouse=True)
def fresh_bank():
    bank.reset()


@pytest.fixture
def tools():
    t = build_session_tools(Session(account_id="ACC-1001", customer_name="Demo Customer"))
    return {tool.name: tool for tool in t}
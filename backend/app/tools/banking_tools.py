from langchain_core.tools import tool

from app.bank.mock_bank import BankError, bank


@tool
def get_balance(account_id: str) -> dict:
    """Get the current balance of a bank account.

    Args:
        account_id: The account ID, e.g. 'ACC-1001'.
    """
    try:
        acc = bank.get_account(account_id)
        return {"account_id": acc.account_id, "balance": acc.balance, "currency": acc.currency}
    except BankError as e:
        return {"error": str(e)}


@tool
def find_beneficiaries(account_id: str, name_query: str = "") -> dict:
    """Find saved beneficiaries (payees) for an account. Leave name_query empty to list all.

    Args:
        account_id: The account ID whose saved beneficiaries to search.
        name_query: Part of the beneficiary's name or nickname, e.g. 'Nimal'.
    """
    try:
        results = bank.find_beneficiaries(account_id, name_query)
        return {"beneficiaries": [b.model_dump() for b in results]}
    except BankError as e:
        return {"error": str(e)}


@tool
def transfer_money(account_id: str, beneficiary_id: str, amount: float, reference: str = "") -> dict:
    """Transfer money from an account to a saved beneficiary.

    Args:
        account_id: The account to send money from.
        beneficiary_id: The beneficiary ID, e.g. 'BEN-01'.
        amount: Amount in LKR.
        reference: Optional payment reference.
    """
    try:
        tx = bank.transfer(account_id, beneficiary_id, amount, reference)
        return tx.model_dump(mode="json")
    except BankError as e:
        return {"error": str(e)}


@tool
def get_transaction_status(transaction_id: str) -> dict:
    """Get the status of a previous transaction.

    Args:
        transaction_id: The transaction ID, e.g. 'TXN-1A2B3C4D'.
    """
    try:
        return bank.get_transaction(transaction_id).model_dump(mode="json")
    except BankError as e:
        return {"error": str(e)}


ALL_TOOLS = [get_balance, find_beneficiaries, transfer_money, get_transaction_status]
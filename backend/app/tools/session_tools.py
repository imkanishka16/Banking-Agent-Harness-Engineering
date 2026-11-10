"""Harnessed tools: bound to a logged-in session and guarded by policy."""
from dataclasses import dataclass

from langchain_core.tools import tool

from app.bank.mock_bank import BankError, bank
from app.harness.tool_policy import check_transfer
from app.harness.content_guard import sanitize_fields


@dataclass(frozen=True)
class Session:
    account_id: str
    customer_name: str


def build_session_tools(session: Session) -> list:
    account_id = session.account_id  # captured here, never chosen by the LLM

    @tool
    def get_balance() -> dict:
        """Get the logged-in customer's current account balance."""
        acc = bank.get_account(account_id)
        return {"balance": acc.balance, "currency": acc.currency}

    @tool
    def find_beneficiaries(name_query: str = "") -> dict:
        """Search the customer's saved beneficiaries. Leave name_query empty to list all.

        Args:
            name_query: Part of the beneficiary's name or nickname, e.g. 'Nimal'.
        """
        results = bank.find_beneficiaries(account_id, name_query)
        beneficiaries, findings = [], []
        for b in results:
            clean, found = sanitize_fields(b.model_dump(), ["name", "nickname"])
            beneficiaries.append(clean)
            findings.extend(found)
        output = {"count": len(beneficiaries), "beneficiaries": beneficiaries}
        if findings:
            output["security_notice"] = (
                "Some fields contained instruction-like text and were removed by the bank's safety filter."
            )
        return output

    @tool
    def transfer_money(beneficiary_id: str, amount: float, reference: str = "") -> dict:
        """Transfer money from the customer's account to one of their saved beneficiaries.

        Args:
            beneficiary_id: The beneficiary ID, e.g. 'BEN-01'.
            amount: Amount in LKR.
            reference: Optional payment reference.
        """
        decision = check_transfer(account_id, beneficiary_id, amount)
        if not decision.allowed:
            return {"blocked_by_policy": decision.code, "reason": decision.reason}
        try:
            return bank.transfer(account_id, beneficiary_id, amount, reference).model_dump(mode="json")
        except BankError as e:
            return {"error": str(e)}

    @tool
    def get_transaction_status(transaction_id: str) -> dict:
        """Get the status of one of the customer's transactions.

        Args:
            transaction_id: The transaction ID, e.g. 'TXN-1A2B3C4D'.
        """
        try:
            tx = bank.get_transaction(transaction_id)
        except BankError:
            return {"error": "Transaction not found."}
        if tx.from_account_id != account_id:
            # Same message as "not found", so we don't confirm other customers' IDs exist
            return {"error": "Transaction not found."}
        return tx.model_dump(mode="json")

    return [get_balance, find_beneficiaries, transfer_money, get_transaction_status]
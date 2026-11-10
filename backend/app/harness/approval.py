"""Human-in-the-loop: which actions need approval, and what the customer sees."""
from app.bank.mock_bank import bank
from app.harness.tool_policy import check_transfer

APPROVAL_REQUIRED_TOOLS = {"transfer_money"}


def build_approval_request(account_id: str, tool_call: dict) -> dict | None:
    """Build the approval card for a transfer.

    Returns None if policy will block the call anyway. There's no point asking
    a human to approve something the rules already forbid.
    All details come from bank records, never from the LLM's text.
    """
    args = tool_call["args"]
    beneficiary_id = str(args.get("beneficiary_id", ""))
    amount = float(args.get("amount", 0))

    if not check_transfer(account_id, beneficiary_id, amount).allowed:
        return None

    ben = bank.beneficiaries[beneficiary_id]
    return {
        "type": "transfer_approval",
        "tool_call_id": tool_call["id"],
        "amount": amount,
        "currency": "LKR",
        "beneficiary_id": ben.beneficiary_id,
        "beneficiary_name": ben.name,
        "bank_name": ben.bank_name,
        "account_number": ben.account_number,
        "reference": args.get("reference", ""),
        "message": f"Send {amount:,.2f} LKR to {ben.name} ({ben.bank_name}, {ben.account_number})?",
    }
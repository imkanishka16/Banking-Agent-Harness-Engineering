"""Deterministic rules checked BEFORE any money moves.

The LLM can be persuaded, confused or injected. These checks cannot.
"""
from dataclasses import dataclass

from app.bank.mock_bank import BankError, bank
from app.config import get_settings


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str
    reason: str


def check_transfer(account_id: str, beneficiary_id: str, amount: float) -> PolicyDecision:
    settings = get_settings()

    if amount <= 0:
        return PolicyDecision(False, "INVALID_AMOUNT", "Amount must be greater than zero.")

    beneficiary = bank.beneficiaries.get(beneficiary_id)
    if beneficiary is None or beneficiary.owner_account_id != account_id:
        return PolicyDecision(False, "UNKNOWN_BENEFICIARY",
                              "Beneficiary is not in this customer's saved beneficiary list.")

    if amount > settings.max_transfer_amount:
        return PolicyDecision(False, "LIMIT_EXCEEDED",
                              f"Amount exceeds the per-transfer limit of {settings.max_transfer_amount:,.0f} LKR.")

    sent_today = bank.total_sent_today(account_id)
    if sent_today + amount > settings.daily_transfer_limit:
        remaining = max(settings.daily_transfer_limit - sent_today, 0)
        return PolicyDecision(False, "DAILY_LIMIT_EXCEEDED",
                              f"Daily transfer limit of {settings.daily_transfer_limit:,.0f} LKR reached. "
                              f"Remaining today: {remaining:,.0f} LKR.")

    try:
        balance = bank.get_account(account_id).balance
    except BankError:
        return PolicyDecision(False, "UNKNOWN_ACCOUNT", "Session account not found.")
    if amount > balance:
        return PolicyDecision(False, "INSUFFICIENT_FUNDS",
                              f"Amount exceeds available balance of {balance:,.0f} LKR.")

    return PolicyDecision(True, "OK", "Transfer passes all policy checks.")
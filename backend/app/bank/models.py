from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

# NOTE: real banking code would use Decimal for money.
# float keeps this demo simple and JSON-friendly.


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Account(BaseModel):
    account_id: str
    owner_name: str
    balance: float
    currency: str = "LKR"


class Beneficiary(BaseModel):
    beneficiary_id: str
    owner_account_id: str  # the customer who saved this beneficiary
    name: str
    bank_name: str
    account_number: str
    nickname: str = ""


class Transaction(BaseModel):
    transaction_id: str
    from_account_id: str
    beneficiary_id: str
    amount: float
    currency: str = "LKR"
    reference: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
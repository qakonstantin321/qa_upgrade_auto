from typing import List, Literal

from src.main.api.models.base_model import BaseModel


class Transaction(BaseModel):
    id: int
    amount: float
    type: Literal["DEPOSIT"]
    timestamp: str
    relatedAccountId: int


class DepositMoneyResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List[Transaction]

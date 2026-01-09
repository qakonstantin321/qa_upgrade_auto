from typing import List, Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.specs.response_specs import ResponseSpecs


class Transaction(BaseModel):
    id: int
    amount: float
    type: ResponseSpecs.TransactionType
    timestamp: str
    relatedAccountId: int


class Account(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List[Transaction]


class GetProfileResponse(BaseModel):
    id: int
    username: str
    password: str
    name: Optional[str]
    role: ResponseSpecs.Role
    accounts: List[Account]

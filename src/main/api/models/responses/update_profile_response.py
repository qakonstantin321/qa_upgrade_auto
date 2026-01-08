from typing import List, Literal

from src.main.api.models.base_model import BaseModel


class Transaction(BaseModel):
    id: int
    amount: float
    type: str
    timestamp: str
    relatedAccountId: int


class Account(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List[Transaction] = []


class Customer(BaseModel):
    id: int
    username: str
    password: str
    name: str
    role: Literal["USER", "ADMIN"]
    accounts: List[Account] = []


class UpdateProfileResponse(BaseModel):
    customer: Customer
    message: str

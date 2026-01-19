from typing import List

from src.main.api.models.base_model import BaseModel
from src.main.api.models.responses.common_models import Transaction


class DepositMoneyResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    transactions: List[Transaction]

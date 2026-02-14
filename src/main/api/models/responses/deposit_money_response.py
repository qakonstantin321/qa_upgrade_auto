from typing import List, Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.models.responses.common_models import Transaction


class DepositMoneyResponse(BaseModel):
    id: int
    accountNumber: str
    balance: float
    depositAmount: Optional[float] = None
    transactionId: Optional[int] = None
    transactions: Optional[List[Transaction]] = None

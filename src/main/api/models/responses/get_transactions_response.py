from typing import List

from pydantic import RootModel

from src.main.api.models.base_model import BaseModel
from src.main.api.specs.response_specs import ResponseSpecs


class Transaction(BaseModel):
    id: int
    amount: float
    type: ResponseSpecs.TransactionType
    timestamp: str
    relatedAccountId: int


class GetTransactionsResponse(RootModel[List[Transaction]]):
    def __len__(self) -> int:
        return len(self.root)

    @property
    def transactions(self) -> List[Transaction]:
        return self.root

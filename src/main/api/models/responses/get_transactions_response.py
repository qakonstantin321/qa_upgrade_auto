from typing import List

from pydantic import RootModel

from src.main.api.models.responses.common_models import Transaction


class GetTransactionsResponse(RootModel[List[Transaction]]):
    def __len__(self) -> int:
        return len(self.root)

    @property
    def transactions(self) -> List[Transaction]:
        return self.root

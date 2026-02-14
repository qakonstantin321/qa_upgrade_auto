from typing import Annotated

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class DepositMoneyRequest(BaseModel):
    accountId: int
    amount: Annotated[float, GeneratingRule(regex=r"^(?:(?:[1-9]\d{0,2}|[1-4]\d{3})(?:\.\d{1,2})?|5000(?:\.0+)?)$")]

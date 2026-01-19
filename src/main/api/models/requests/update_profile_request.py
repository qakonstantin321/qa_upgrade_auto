from typing import Annotated

from src.main.api.generators.generating_rule import GeneratingRule
from src.main.api.models.base_model import BaseModel


class UpdateProfileRequest(BaseModel):
    name: Annotated[str, GeneratingRule(regex=r"^[A-Za-z]{1,15} [A-Za-z]{1,15}$")]

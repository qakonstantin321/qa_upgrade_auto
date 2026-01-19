from typing import List, Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.models.responses.common_models import Account
from src.main.api.specs.response_specs import ResponseSpecs


class GetProfileResponse(BaseModel):
    id: int
    username: str
    password: str
    name: Optional[str]
    role: ResponseSpecs.Role
    accounts: List[Account]

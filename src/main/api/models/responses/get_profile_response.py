from typing import Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.specs.response_specs import ResponseSpecs


class GetProfileResponse(BaseModel):
    id: int
    username: str
    name: Optional[str]
    role: ResponseSpecs.Role

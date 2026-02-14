from typing import Any, Dict, List, Optional

from src.main.api.models.base_model import BaseModel
from src.main.api.specs.response_specs import ResponseSpecs


class CreateUserResponse(BaseModel):
    id: int
    username: str
    password: Optional[str] = None
    name: Optional[str] = None
    role: ResponseSpecs.Role
    accounts: List[Dict[str, Any]] = []

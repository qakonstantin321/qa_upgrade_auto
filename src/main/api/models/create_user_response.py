from typing import Any, Dict, List, Optional

from src.main.api.models.base_model import BaseModel


class CreateUserResponse(BaseModel):
    id: int
    username: str
    password: str
    name: Optional[str]
    role: str
    accounts: List[Dict[str, Any]]

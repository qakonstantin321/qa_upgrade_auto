from typing import List

from src.main.api.models.base_model import BaseModel
from src.main.api.models.responses.common_models import Account
from src.main.api.specs.response_specs import ResponseSpecs


class Customer(BaseModel):
    id: int
    username: str
    password: str
    name: str
    role: ResponseSpecs.Role
    accounts: List[Account] = []


class UpdateProfileResponse(BaseModel):
    customer: Customer
    message: str

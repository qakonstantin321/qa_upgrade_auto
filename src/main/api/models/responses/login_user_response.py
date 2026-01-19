from src.main.api.models.base_model import BaseModel
from src.main.api.specs.response_specs import ResponseSpecs


class LoginUserResponse(BaseModel):
    username: str
    role: ResponseSpecs.Role

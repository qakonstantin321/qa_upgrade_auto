from src.main.api.models.base_model import BaseModel
from src.main.api.specs.response_specs import ResponseSpecs


class UpdateProfileResponse(BaseModel):
    id: int
    username: str
    name: str
    role: ResponseSpecs.Role

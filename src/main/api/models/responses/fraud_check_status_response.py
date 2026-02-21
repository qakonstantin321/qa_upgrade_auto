from src.main.api.models.base_model import BaseModel


class FraudCheckStatusResponse(BaseModel):
    status: str
    note: str
    transactionId: int

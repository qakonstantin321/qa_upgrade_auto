from src.main.api.models.base_model import BaseModel


class TransferMoneyRequest(BaseModel):
    senderAccountId: int
    receiverAccountId: int
    amount: float

from dataclasses import dataclass
from enum import Enum
from typing import List

from src.main.api.models.base_model import BaseModel
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.requests.login_user_request import LoginUserRequest
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.requests.update_profile_request import UpdateProfileRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.models.responses.create_user_response import CreateUserResponse
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse
from src.main.api.models.responses.login_user_response import LoginUserResponse
from src.main.api.models.responses.transfer_money_response import TransferMoneyResponse
from src.main.api.models.responses.update_profile_response import UpdateProfileResponse


@dataclass(frozen=True)
class EndpointConfig:
    url: str
    request_model: type[BaseModel] | type[List[BaseModel]] | None
    response_model: type[BaseModel] | type[List[BaseModel]] | None


class Endpoint(Enum):
    ADMIN_CREATE_USER = EndpointConfig(
        url='/admin/users',
        request_model=CreateUserRequest,
        response_model=CreateUserResponse
    )

    ADMIN_DELETE_USER = EndpointConfig(
        url='/admin/users',
        request_model=None,
        response_model=None
    )

    ADMIN_GET_ALL_USERS = EndpointConfig(
        url='/admin/users',
        request_model=None,
        response_model=List[CreateUserRequest]
    )

    LOGIN_USER = EndpointConfig(
        url='/auth/login',
        request_model=LoginUserRequest,
        response_model=LoginUserResponse
    )

    CREATE_ACCOUNT = EndpointConfig(
        url='/accounts',
        request_model=None,
        response_model=CreateAccountResponse
    )

    GET_CUSTOMER_ACCOUNTS = EndpointConfig(
        url='/customer/accounts',
        request_model=None,
        response_model=List[CreateAccountResponse]
    )

    DEPOSIT_MONEY = EndpointConfig(
        url='/accounts/deposit',
        request_model=DepositMoneyRequest,
        response_model=DepositMoneyResponse
    )

    TRANSFER_MONEY = EndpointConfig(
        url='/accounts/transfer',
        request_model=TransferMoneyRequest,
        response_model=TransferMoneyResponse
    )

    UPDATE_PROFILE = EndpointConfig(
        url='/customer/profile',
        request_model=UpdateProfileRequest,
        response_model=UpdateProfileResponse
    )

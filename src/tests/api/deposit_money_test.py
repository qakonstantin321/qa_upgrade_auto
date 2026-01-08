from typing import Union

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse


@pytest.mark.api
class TestDepositMoney:
    def test_valid_deposit_money(self, user_request: CreateUserRequest,
                                 create_account: CreateAccountResponse,
                                 api_manager: ApiManager):
        api_manager.user_steps.deposit_money(user_request, create_account)

    @pytest.mark.parametrize(
        argnames='balance, error_value',
        argvalues=[
            (-100, 'Deposit amount must be at least 0.01'),
            (0.0, 'Deposit amount must be at least 0.01'),
            (5001, 'Deposit amount cannot exceed 5000')
        ]
    )
    def test_invalid_deposit_money(self, user_request: CreateUserRequest,
                                   create_account: CreateAccountResponse,
                                   api_manager: ApiManager,
                                   balance: Union[float, int], error_value: str):
        deposit_money_request = DepositMoneyRequest(id=create_account.id, balance=balance)
        api_manager.user_steps.invalid_deposit_money(user_request, deposit_money_request, error_value)

    def test_deposit_money_non_exist_account(self, user_request: CreateUserRequest,
                                             api_manager: ApiManager):
        deposit_money_request = DepositMoneyRequest(id=41214341, balance=RandomData.get_balance())
        api_manager.user_steps.deposit_money_invalid_account(user_request, deposit_money_request)

    def test_deposit_money_another_user_account(self,
                                                create_account: CreateAccountResponse,
                                                api_manager: ApiManager):
        new_user = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(new_user)

        deposit_money_request = DepositMoneyRequest(id=create_account.id, balance=RandomData.get_balance())
        api_manager.user_steps.deposit_money_invalid_account(new_user, deposit_money_request)

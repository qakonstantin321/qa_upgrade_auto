from typing import Union

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.specs.response_specs import ResponseSpecs


DEPOSIT_MONEY_RESPONSE_KEY = "deposit_money_response"


@pytest.mark.api
class TestDepositMoney:
    @pytest.mark.check_transactions_count(account_id_source="create_account.id", expected_before=0, expected_after=1)
    @pytest.mark.check_deposit_transaction_match(account_id_source="create_account.id")
    @pytest.mark.parametrize('deposit_money_request', [RandomModelGenerator.generate(DepositMoneyRequest)])
    def test_valid_deposit_money(self, api_manager: ApiManager,
                                 user_request: CreateUserRequest,
                                 create_account: CreateAccountResponse,
                                 deposit_money_request: DepositMoneyRequest,
                                 request: pytest.FixtureRequest):
        deposit_money_resp = api_manager.user_steps.deposit_money(user_request, create_account, deposit_money_request)
        request.node.user_properties[DEPOSIT_MONEY_RESPONSE_KEY] = deposit_money_resp

    @pytest.mark.check_transactions_count(account_id_source="create_account.id", expected_after=0)
    @pytest.mark.parametrize(
        argnames='balance, error_value',
        argvalues=[
            (-100, ResponseSpecs.DEPOSIT_MIN_AMOUNT),
            (0.0, ResponseSpecs.DEPOSIT_MIN_AMOUNT),
            (5001, ResponseSpecs.DEPOSIT_MAX_AMOUNT)
        ]
    )
    def test_invalid_deposit_money(self, api_manager: ApiManager,
                                   user_request: CreateUserRequest,
                                   create_account: CreateAccountResponse,
                                   balance: Union[float, int], error_value: str):
        deposit_money_req = DepositMoneyRequest(id=create_account.id, balance=balance)
        api_manager.user_steps.invalid_deposit_money(user_request, deposit_money_req, error_value)

    def test_deposit_money_non_existing_account(self, api_manager: ApiManager,
                                                user_request: CreateUserRequest):
        non_existing_account_id: int = 41214341
        deposit_money_req = DepositMoneyRequest(id=non_existing_account_id, balance=RandomData.get_balance())
        api_manager.user_steps.deposit_money_invalid_account(user_request, deposit_money_req)
        api_manager.user_steps.get_transactions_forbidden(user_request, non_existing_account_id)

    @pytest.mark.check_transactions_count(account_id_source="create_account.id", expected_after=0)
    def test_deposit_money_another_user_account(self, api_manager: ApiManager,
                                                create_account: CreateAccountResponse,
                                                new_user_request: CreateUserRequest):
        api_manager.admin_steps.create_user(new_user_request)

        deposit_money_req = DepositMoneyRequest(id=create_account.id, balance=RandomData.get_balance())
        api_manager.user_steps.deposit_money_invalid_account(new_user_request, deposit_money_req)

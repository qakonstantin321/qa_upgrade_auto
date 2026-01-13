from typing import Union

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse
from src.main.api.models.responses.get_transactions_response import GetTransactionsResponse
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestDepositMoney:
    def test_valid_deposit_money(self, user_request: CreateUserRequest,
                                 create_account: CreateAccountResponse,
                                 api_manager: ApiManager):
        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request,
                                                                                                 create_account.id)
        assert not get_transactions_resp.transactions

        deposit_money_resp: DepositMoneyResponse = api_manager.user_steps.deposit_money(user_request,
                                                                                        create_account)

        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request,
                                                                                                 deposit_money_resp.id)
        assert len(get_transactions_resp.transactions) == 1
        ModelAssertions(deposit_money_resp.transactions[0], get_transactions_resp.transactions[0]).match()

    @pytest.mark.parametrize(
        argnames='balance, error_value',
        argvalues=[
            (-100, ResponseSpecs.DEPOSIT_MIN_AMOUNT),
            (0.0, ResponseSpecs.DEPOSIT_MIN_AMOUNT),
            (5001, ResponseSpecs.DEPOSIT_MAX_AMOUNT)
        ]
    )
    def test_invalid_deposit_money(self, user_request: CreateUserRequest,
                                   create_account: CreateAccountResponse,
                                   api_manager: ApiManager,
                                   balance: Union[float, int], error_value: str):
        deposit_money_req = DepositMoneyRequest(id=create_account.id, balance=balance)
        api_manager.user_steps.invalid_deposit_money(user_request, deposit_money_req, error_value)

        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request,
                                                                                                 create_account.id)
        assert not get_transactions_resp.transactions

    def test_deposit_money_non_existing_account(self, user_request: CreateUserRequest,
                                                api_manager: ApiManager):
        non_existing_account_id: int = 41214341
        deposit_money_req = DepositMoneyRequest(id=non_existing_account_id, balance=RandomData.get_balance())
        api_manager.user_steps.deposit_money_invalid_account(user_request, deposit_money_req)
        api_manager.user_steps.get_transactions_forbidden(user_request, non_existing_account_id)

    def test_deposit_money_another_user_account(self,
                                                user_request: CreateUserRequest,
                                                create_account: CreateAccountResponse,
                                                api_manager: ApiManager):
        new_user = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(new_user)

        deposit_money_req = DepositMoneyRequest(id=create_account.id, balance=RandomData.get_balance())
        api_manager.user_steps.deposit_money_invalid_account(new_user, deposit_money_req)

        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request,
                                                                                                 create_account.id)
        assert not get_transactions_resp.transactions

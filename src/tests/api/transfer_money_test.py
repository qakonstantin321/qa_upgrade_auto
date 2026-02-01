from typing import Union

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestTransferMoney:
    @pytest.mark.check_all_users_change(delta=2, username_source="new_user_request.username", should_exist=True)
    @pytest.mark.check_transfer_transaction(
        receiver_user_source="user_2",
        receiver_account_id_source="account_user_2.id",
        sender_account_id_source="deposit_account.id"
    )
    def test_transfer_money_different_users(self, api_manager: ApiManager,
                                            user_request: CreateUserRequest,
                                            deposit_account: DepositMoneyResponse,
                                            new_user_request: CreateUserRequest,
                                            request: pytest.FixtureRequest):
        user_2 = api_manager.admin_steps.create_user(new_user_request)
        account_user_2 = api_manager.user_steps.create_user_account(user_2)
        request.node.user_properties['user_2'] = user_2
        request.node.user_properties['account_user_2'] = account_user_2

        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account.id,
                                            receiverAccountId=account_user_2.id,
                                            amount=deposit_account.balance)
        transfer_resp = api_manager.user_steps.transfer_money(user_request, transfer_req)
        request.node.user_properties['transfer_response'] = transfer_resp

    @pytest.mark.check_accounts_change(delta=2)
    @pytest.mark.check_transfer_transaction(
        receiver_user_source="user_request",
        receiver_account_id_source="user_account_2.id",
        sender_account_id_source="deposit_account.id"
    )
    def test_transfer_money_accounts_same_user(self, api_manager: ApiManager,
                                               user_request: CreateUserRequest,
                                               deposit_account: DepositMoneyResponse,
                                               request: pytest.FixtureRequest):
        user_account_2 = api_manager.user_steps.create_user_account(user_request)
        request.node.user_properties['user_account_2'] = user_account_2

        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account.id,
                                            receiverAccountId=user_account_2.id,
                                            amount=deposit_account.balance)
        transfer_resp = api_manager.user_steps.transfer_money(user_request, transfer_req)
        request.node.user_properties['transfer_response'] = transfer_resp

    @pytest.mark.check_transactions_count(account_id_source="deposit_account_20000_rubbles.id", expected_after=4)
    @pytest.mark.parametrize(
        argnames='amount, error_value',
        argvalues=[
            (-100, ResponseSpecs.TRANSFER_MIN_AMOUNT),
            (9999999, ResponseSpecs.TRANSFER_MAX_AMOUNT),
            (10001, ResponseSpecs.TRANSFER_MAX_AMOUNT)
        ]
    )
    @pytest.mark.check_accounts_change(delta=2)
    def test_invalid_transfer_money(self, api_manager: ApiManager,
                                    user_request: CreateUserRequest,
                                    deposit_account_20000_rubbles: DepositMoneyResponse,
                                    amount: Union[float, int], error_value: str):
        receiver_account = api_manager.user_steps.create_user_account(user_request)
        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account_20000_rubbles.id,
                                            receiverAccountId=receiver_account.id,
                                            amount=amount)
        api_manager.user_steps.invalid_transfer_money(user_request, transfer_req, error_value)

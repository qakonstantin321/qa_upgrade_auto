from typing import Union

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse
from src.main.api.models.responses.get_transactions_response import GetTransactionsResponse
from src.main.api.models.responses.transfer_money_response import TransferMoneyResponse
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestTransferMoney:
    def test_transfer_money_different_users(self, user_request: CreateUserRequest,
                                            deposit_account: DepositMoneyResponse,
                                            api_manager: ApiManager):
        user_1, account_user_1 = user_request, deposit_account
        user_2 = api_manager.admin_steps.create_user(RandomModelGenerator.generate(CreateUserRequest))
        account_user_2 = api_manager.user_steps.create_user_account(user_2)

        transfer_req = TransferMoneyRequest(senderAccountId=account_user_1.id,
                                            receiverAccountId=account_user_2.id,
                                            amount=account_user_1.balance)
        transfer_resp: TransferMoneyResponse = api_manager.user_steps.transfer_money(user_1,
                                                                                     transfer_req)

        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_2,
                                                                                                 account_user_2.id)
        assert len(get_transactions_resp.transactions) == 1
        tr = get_transactions_resp.transactions[-1]
        assert tr.amount == transfer_resp.amount
        assert tr.type == ResponseSpecs.TransactionType.TRANSFER_IN.value
        assert tr.relatedAccountId == transfer_resp.senderAccountId

    def test_transfer_money_accounts_same_user(self, user_request: CreateUserRequest,
                                               deposit_account: DepositMoneyResponse,
                                               api_manager: ApiManager):
        user_account_2 = api_manager.user_steps.create_user_account(user_request)

        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account.id,
                                            receiverAccountId=user_account_2.id,
                                            amount=deposit_account.balance)
        transfer_resp: TransferMoneyResponse = api_manager.user_steps.transfer_money(
            user_request=user_request,
            transfer_money_request=transfer_req
        )
        assert transfer_resp.amount == transfer_req.amount
        assert transfer_resp.senderAccountId == transfer_req.senderAccountId
        assert transfer_resp.receiverAccountId == transfer_req.receiverAccountId
        assert transfer_resp.message == 'Transfer successful'

        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request,
                                                                                                 user_account_2.id)
        assert len(get_transactions_resp.transactions) == 1
        tr = get_transactions_resp.transactions[-1]
        assert tr.amount == transfer_resp.amount
        assert tr.type == ResponseSpecs.TransactionType.TRANSFER_IN.value
        assert tr.relatedAccountId == transfer_resp.senderAccountId

    @pytest.mark.parametrize(
        argnames='amount, error_value',
        argvalues=[
            (-100, ResponseSpecs.TRANSFER_MIN_AMOUNT),
            (9999999, ResponseSpecs.TRANSFER_MAX_AMOUNT),
            (10001, ResponseSpecs.TRANSFER_MAX_AMOUNT)
        ]
    )
    def test_invalid_transfer_money(self, user_request: CreateUserRequest,
                                    deposit_account_20000_rubbles: DepositMoneyResponse,
                                    api_manager: ApiManager,
                                    amount: Union[float, int], error_value: str):
        receiver_account = api_manager.user_steps.create_user_account(user_request)
        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account_20000_rubbles.id,
                                            receiverAccountId=receiver_account.id,
                                            amount=amount)

        api_manager.user_steps.invalid_transfer_money(user_request,
                                                      transfer_req,
                                                      error_value)

        get_transactions_resp: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request,
                                                                                                 deposit_account_20000_rubbles.id)
        assert len(get_transactions_resp.transactions) == 4

from typing import Union

import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse
from src.main.api.models.responses.get_transactions_response import GetTransactionsResponse
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.transfer_page import TransferMoneyPage
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
@pytest.mark.usefixtures("user_session_extension", "browser_match_guard")
class TestTransferMoney:
    @pytest.mark.user_session
    def test_transfer_money_same_user(self, api_manager: ApiManager, page: Page,
                                      user_request: CreateUserRequest,
                                      deposit_account: DepositMoneyResponse):
        user_account_2 = api_manager.user_steps.create_user_account(user_request)
        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account.id,
                                            receiverAccountId=user_account_2.id,
                                            amount=deposit_account.balance)

        dashboard_page = UserDashboard(page).open()
        dashboard_page.make_transfer()
        transfer_page = dashboard_page.get_page(TransferMoneyPage)
        expect(transfer_page.transfer_money_panel_text).to_be_visible()
        transfer_page.transfer(transfer_req, name=user_request.username)
        transfer_page.check_alert_message_and_accept(
            BankAlert.MONEY_TRANSFERED.value.format(amount=transfer_req.amount,
                                                    account_id=transfer_req.receiverAccountId))

        transfer_resp: GetTransactionsResponse = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_transactions(user_request, user_account_2.id),
            condition=lambda response: len(response.transactions) == 1
        )
        assert len(transfer_resp.transactions) == 1
        tr = transfer_resp.transactions[-1]
        assert tr.amount == transfer_req.amount
        assert tr.type == ResponseSpecs.TransactionType.TRANSFER_IN.value
        assert transfer_req.senderAccountId == tr.relatedAccountId

    @pytest.mark.parametrize(
        argnames='amount, error_value',
        argvalues=[
            (-100, BankAlert.NEGATIVE_TRANSFER),
            (9999999, BankAlert.EXCEED_10000_TRANSFER),
            (10001, BankAlert.EXCEED_10000_TRANSFER)
        ]
    )
    @pytest.mark.user_session
    def test_invalid_transfer_money(self, page: Page, user_request: CreateUserRequest,
                                    deposit_account_20000_rubbles: DepositMoneyResponse,
                                    api_manager: ApiManager,
                                    amount: Union[float, int], error_value: str):
        receiver_account = api_manager.user_steps.create_user_account(user_request)
        transfer_req = TransferMoneyRequest(senderAccountId=deposit_account_20000_rubbles.id,
                                            receiverAccountId=receiver_account.id,
                                            amount=amount)

        transfer_page = TransferMoneyPage(page).open()
        transfer_page.transfer(transfer_req, name=user_request.username)
        transfer_page.check_alert_message_and_accept(error_value)

        transfer_resp: GetTransactionsResponse = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_transactions(user_request, deposit_account_20000_rubbles.id),
            condition=lambda response: len(response.transactions) == 4
        )
        assert len(transfer_resp.transactions) == 4

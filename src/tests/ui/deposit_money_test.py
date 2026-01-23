from typing import Union

import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.models.responses.get_transactions_response import GetTransactionsResponse
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.deposit_money import DepositMoneyPage
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestDepositMoney:
    @pytest.mark.user_session
    @pytest.mark.parametrize('deposit_money_request', [RandomModelGenerator.generate(DepositMoneyRequest)])
    def test_user_deposit_money(self, api_manager: ApiManager, page: Page,
                                user_request: CreateUserRequest,
                                deposit_money_request: DepositMoneyRequest):
        user_account: CreateAccountResponse = api_manager.user_steps.create_user_account(user_request)
        deposit_money_request.id = user_account.id

        dashboard_page = UserDashboard(page).open()
        dashboard_page.deposit_money()
        deposit_page = dashboard_page.get_page(DepositMoneyPage)
        expect(deposit_page.deposit_money_panel_text).to_be_visible()
        deposit_page.deposit(deposit_money_request)
        deposit_page.check_alert_message_and_accept(
            BankAlert.ACCOUNT_DEPOSITED.value.format(amount=deposit_money_request.balance,
                                                     account_id=deposit_money_request.id))

        resp: GetTransactionsResponse = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_transactions(user_request, user_account.id),
            condition=lambda response: len(response.transactions) == 1
        )
        assert len(resp.transactions) == 1
        assert resp.transactions[0].amount == deposit_money_request.balance
        assert resp.transactions[0].relatedAccountId == deposit_money_request.id

    @pytest.mark.parametrize(
        argnames='balance, error_value',
        argvalues=[
            (-100, BankAlert.INVALID_AMOUNT),
            (0, BankAlert.INVALID_AMOUNT),
            (5001, BankAlert.INVALID_AMOUNT_MORE_5000)
        ]
    )
    @pytest.mark.user_session
    @pytest.mark.xfail(
        reason="Dialog window doesn't appear for invalid amounts",
        strict=True
    )
    def test_invalid_deposit_money(self, page: Page, user_request: CreateUserRequest,
                                   create_account: CreateAccountResponse,
                                   api_manager: ApiManager,
                                   balance: Union[float, int], error_value: str):
        deposit_money_request = DepositMoneyRequest(id=create_account.id, balance=balance)

        deposit_page = DepositMoneyPage(page).open()
        deposit_page.deposit(deposit_money_request)
        deposit_page.check_alert_message_and_accept(error_value, 1000)

        resp: GetTransactionsResponse = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_transactions(user_request, create_account.id),
            condition=lambda response: not response.transactions
        )
        assert not resp.transactions

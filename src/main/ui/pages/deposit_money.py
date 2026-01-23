from typing import Union

from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.ui.pages.base_page import BasePage


class DepositMoneyPage(BasePage):
    @property
    def deposit_money_panel_text(self):
        return self.page.get_by_text("💰 Deposit Money")

    @property
    def deposit_button(self):
        return self.page.get_by_role("button", name="💵 Deposit")

    def account_select_by_id(self, account_id: int):
        return self.page.locator("select.account-selector").select_option(str(account_id))

    def amount_input(self, amount: Union[float, int]):
        return self.page.locator("input.deposit-input").fill(str(amount))

    def url(self):
        return "/deposit"

    def deposit(self, deposit_money_request: DepositMoneyRequest):
        self.account_select_by_id(deposit_money_request.id)
        self.amount_input(deposit_money_request.balance)
        self.deposit_button.click()
        return self

from typing import Union

from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.ui.pages.base_page import BasePage


class TransferMoneyPage(BasePage):
    @property
    def transfer_money_panel_text(self):
        return self.page.get_by_text("🔄 Make a Transfer")

    @property
    def transfer_button(self):
        return self.page.get_by_role("button", name="🚀 Send Transfer")

    def account_select_by_id(self, account_id: int):
        return self.page.locator("select.account-selector").select_option(str(account_id))

    def recipient_name_input(self, name: str):
        return self.page.locator("input[placeholder='Enter recipient name']").fill(name)

    def recipient_account_number_input(self, account_id: str):
        return self.page.locator("input[placeholder='Enter recipient account number']").fill(account_id)

    def amount_input(self, amount: Union[float, int]):
        return self.page.locator("input[placeholder='Enter amount']").fill(str(amount))

    def confirm_details_checkbox(self):
        return self.page.get_by_role("checkbox", name="Confirm details are correct").check()

    def url(self):
        return "/transfer"

    def transfer(self, transfer_money_request: TransferMoneyRequest, name: str, account_number: str):
        self.account_select_by_id(transfer_money_request.senderAccountId)
        self.recipient_name_input(name)
        self.recipient_account_number_input(account_number)
        self.amount_input(transfer_money_request.amount)
        self.confirm_details_checkbox()
        self.transfer_button.click()
        return self

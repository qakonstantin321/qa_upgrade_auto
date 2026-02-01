from playwright.sync_api import expect

from src.main.ui.pages.base_page import BasePage


class UserDashboard(BasePage):
    @property
    def welcome_text(self):
        return self.page.get_by_text("User Dashboard")

    @property
    def create_new_account_button(self):
        return self.page.get_by_role("button", name="➕ Create New Account")

    @property
    def deposit_money_button(self):
        return self.page.get_by_role("button", name="💰 Deposit Money")

    @property
    def make_transfer_button(self):
        return self.page.get_by_role("button", name="🔄 Make a Transfer")

    @property
    def profile_header(self):
        return self.page.locator("div.user-info")

    def url(self):
        return "/dashboard"

    def create_new_account(self):
        self.create_new_account_button.click()
        return self

    def deposit_money(self):
        self.deposit_money_button.click()
        return self

    def make_transfer(self):
        self.make_transfer_button.click()
        return self

    def edit_profile(self):
        self.profile_header.click()
        return self

    def check_page_is_visible(self):
        expect(self.welcome_text).to_be_visible()
        return self

import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestCreateAccount:
    @pytest.mark.user_session
    def test_user_can_create_account(self, api_manager: ApiManager, page: Page, user_request: CreateUserRequest):
        dashboard_page = UserDashboard(page).open()
        expect(dashboard_page.welcome_text).to_be_visible()
        dashboard_page = dashboard_page.create_new_account()
        dashboard_page.check_alert_message_and_accept(BankAlert.NEW_ACCOUNT_CREATED)

        user_accounts = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_all_accounts(user_request),
            condition=lambda accounts: len(accounts) == 1
        )
        assert len(user_accounts) == 1
        assert user_accounts[0] and user_accounts[0].balance == 0

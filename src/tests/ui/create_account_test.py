import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
@pytest.mark.usefixtures("user_session_extension", "browser_match_guard")
class TestCreateAccount:
    @pytest.mark.user_session
    @pytest.mark.check_accounts_change(delta=1)
    def test_user_can_create_account(self, api_manager: ApiManager, page: Page, user_request: CreateUserRequest):
        UserDashboard(page).open() \
            .check_page_is_visible() \
            .create_new_account() \
            .check_alert_message_and_accept(BankAlert.NEW_ACCOUNT_CREATED)

        user_accounts = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_all_accounts(user_request),
            condition=lambda accounts: len(accounts) == 1
        )
        assert len(user_accounts) == 1
        assert user_accounts[0] and user_accounts[0].balance == 0

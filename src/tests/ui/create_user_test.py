import pytest
from playwright.sync_api import Page

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.bank_alert import BankAlert


@pytest.mark.ui
@pytest.mark.usefixtures("admin_session_autologin", "browser_match_guard")
class TestCreateUser:
    @pytest.mark.admin_session
    @pytest.mark.entity_will_be_created("new_user_request")
    @pytest.mark.check_all_users_change(delta=1, username_source="new_user_request.username")
    def test_admin_can_create_user(self, page: Page, api_manager: ApiManager, new_user_request: CreateUserRequest):
        AdminPanel(page).open() \
            .check_page_is_visible() \
            .create_user(new_user_request.username, new_user_request.password) \
            .check_alert_message_and_accept(BankAlert.USER_CREATED_SUCCESSFULLY) \
            .wait_for_username(new_user_request.username)

        created_user = next(
            u for u in api_manager.admin_steps.get_all_users()
            if u.username == new_user_request.username
        )
        ModelAssertions(new_user_request, created_user).match()

    @pytest.mark.admin_session
    @pytest.mark.check_all_users_change(delta=0, username_source="new_user_request.username", should_exist=False)
    def test_admin_cannot_create_user_with_invalid_data(self, page: Page):
        new_user_request: CreateUserRequest = CreateUserRequest(username=RandomData.get_username(2),
                                                                password=RandomData.get_password(),
                                                                role=ResponseSpecs.Role.USER)
        AdminPanel(page).open() \
            .check_page_is_visible() \
            .create_user(new_user_request.username, new_user_request.password) \
            .check_alert_message_and_accept(BankAlert.USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS) \
            .check_user_is_visible(new_user_request.username)

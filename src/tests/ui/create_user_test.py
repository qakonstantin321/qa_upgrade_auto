import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.bank_alert import BankAlert


@pytest.mark.ui
class TestCreateUser:
    @pytest.mark.admin_session
    @pytest.mark.parametrize('new_user_request', [RandomModelGenerator.generate(CreateUserRequest)])
    def test_admin_can_create_user(self, page: Page, api_manager: ApiManager, new_user_request: CreateUserRequest):
        api_manager.admin_steps.cleanup_objects.append(new_user_request)

        admin_page = AdminPanel(page).open()
        expect(admin_page.admin_panel_text).to_be_visible()
        admin_page.create_user(new_user_request.username, new_user_request.password)
        admin_page.check_alert_message_and_accept(BankAlert.USER_CREATED_SUCCESSFULLY)
        admin_page.wait_for_username(new_user_request.username)

        created_user = next(
            u for u in api_manager.admin_steps.get_all_users()
            if u.username == new_user_request.username
        )
        ModelAssertions(new_user_request, created_user).match()

    @pytest.mark.admin_session
    def test_admin_cannot_create_user_with_invalid_data(self, page: Page, api_manager: ApiManager):
        new_user_request: CreateUserRequest = CreateUserRequest(username=RandomData.get_username(2),
                                                                password=RandomData.get_password(),
                                                                role=ResponseSpecs.Role.USER)
        admin_page = AdminPanel(page).open()
        expect(admin_page.admin_panel_text).to_be_visible()

        admin_page = admin_page.create_user(new_user_request.username, new_user_request.password)
        admin_page.check_alert_message_and_accept(BankAlert.USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS)
        assert not any(u.username == new_user_request.username for u in admin_page.get_all_users())
        assert not any(u.username == new_user_request.username for u in api_manager.admin_steps.get_all_users())

import pytest
from playwright.sync_api import Page, expect

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.responses.get_profile_response import GetProfileResponse
from src.main.ui.pages.bank_alert import BankAlert
from src.main.ui.pages.edit_profile_page import EditProfilePage
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
class TestUpdateProfile:
    @pytest.mark.user_session
    def test_update_profile(self, api_manager: ApiManager, page: Page, user_request: CreateUserRequest):
        name: str = RandomData.get_profile_name()

        dashboard_page = UserDashboard(page).open()
        dashboard_page.edit_profile()
        edit_profile_page = dashboard_page.get_page(EditProfilePage)
        expect(edit_profile_page.edit_profile_panel_text).to_be_visible()
        edit_profile_page.edit_profile_name(name)
        edit_profile_page.check_alert_message_and_accept(BankAlert.NAME_UPDATED)

        get_profile_resp: GetProfileResponse = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_profile(user_request),
            condition=lambda profile: profile.name == name
        )
        assert get_profile_resp.name == name

    @pytest.mark.user_session
    def test_invalid_update_profile(self, page: Page,
                                    user_request: CreateUserRequest,
                                    api_manager: ApiManager):
        name: str = RandomData.get_profile_name()[:1]
        edit_profile_page = EditProfilePage(page).open()
        edit_profile_page.edit_profile_name(name)
        edit_profile_page.check_alert_message_and_accept(BankAlert.INVALID_NAME)

        get_profile_resp: GetProfileResponse = api_manager.user_steps.wait_for_condition(
            func=lambda: api_manager.user_steps.get_profile(user_request),
            condition=lambda profile: profile.name is None
        )
        assert get_profile_resp.name is None

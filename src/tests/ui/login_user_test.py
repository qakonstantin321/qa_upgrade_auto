import pytest
from playwright.sync_api import Page, expect

from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.login_page import LoginPage
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
@pytest.mark.browsers("webkit")
class TestLoginUser:
    def test_admin_can_login_with_correct_data(self, page: Page, admin_user_request: CreateUserRequest):
        login_page = LoginPage(page).open()
        login_page.login(admin_user_request.username, admin_user_request.password)
        admin_page = login_page.get_page(AdminPanel)
        expect(admin_page.admin_panel_text).to_be_visible()

    def test_user_can_login_with_correct_data(self, page: Page, user_request: CreateUserRequest):
        login_page = LoginPage(page).open()
        login_page.login(user_request.username, user_request.password)
        user_dashboard = login_page.get_page(UserDashboard)
        expect(user_dashboard.welcome_text).to_be_visible()

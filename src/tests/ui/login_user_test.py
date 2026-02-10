import pytest
from playwright.sync_api import Page

from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.ui.pages.admin_panel import AdminPanel
from src.main.ui.pages.login_page import LoginPage
from src.main.ui.pages.user_dashboard import UserDashboard


@pytest.mark.ui
@pytest.mark.browsers("webkit")
class TestLoginUser:
    def test_admin_can_login_with_correct_data(self, page: Page, admin_user_request: CreateUserRequest):
        LoginPage(page).open() \
            .login(admin_user_request.username, admin_user_request.password) \
            .get_page(AdminPanel) \
            .check_page_is_visible()

    def test_user_can_login_with_correct_data(self, page: Page, user_request: CreateUserRequest):
        LoginPage(page).open() \
            .login(user_request.username, user_request.password) \
            .get_page(UserDashboard) \
            .check_page_is_visible()

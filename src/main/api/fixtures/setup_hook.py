import pytest
from playwright.sync_api import Page

from src.main.api.classes.session_storage import SessionStorage
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.utils.normalize_browsers import norm_browser_name
from src.main.ui.pages.login_page import LoginPage


@pytest.fixture
def user_session_extension(request: pytest.FixtureRequest, user_factory):
    SessionStorage.clear()

    mark = request.node.get_closest_marker("user_session")
    if not mark:
        return

    count: int = max(int(mark.args[0]) if mark.args else 0, 1)
    auth_index: int = int(mark.kwargs.get("auth", 0))

    users: list[CreateUserRequest] = [user_factory() for _ in range(count)]
    page: Page = request.getfixturevalue("page")
    LoginPage(page).auth_as_user(users[auth_index])


@pytest.fixture
def admin_session_autologin(
        request: pytest.FixtureRequest,
        admin_user_request: CreateUserRequest
):
    if not request.node.get_closest_marker("admin_session"):
        return
    page: Page = request.getfixturevalue("page")
    LoginPage(page).auth_as_user(admin_user_request)


@pytest.fixture
def browser_match_guard(request: pytest.FixtureRequest):
    if request.node.get_closest_marker("api"):
        return

    mark = request.node.get_closest_marker("browsers")
    if not mark:
        return

    allowed = {norm_browser_name(str(x)) for x in (mark.args or ())}
    if not allowed:
        return

    try:
        request.getfixturevalue("browser_name")
    except pytest.FixtureLookupError:
        return

    # No runtime skip here: we filter browsers at collection-time in root conftest.py,
    # so we don't pollute reports with SKIPPED.
    return

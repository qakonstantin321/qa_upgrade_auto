import pytest
from playwright.sync_api import Page

from src.main.api.classes.session_storage import SessionStorage
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.utils.normalize_browsers import norm_browser_name
from src.main.ui.pages.login_page import LoginPage


@pytest.fixture(autouse=True)
def clear_session_storage_for_api(request):
    is_api_test = request.node.get_closest_marker("api") is not None
    if is_api_test:
        SessionStorage.clear()
    yield
    if is_api_test:
        SessionStorage.clear()

@pytest.fixture(autouse=True)
def user_session_extension(request, user_factory):
    SessionStorage.clear()

    mark = request.node.get_closest_marker("user_session")
    if not mark:
        return

    count: int = max(int(mark.args[0]) if mark.args else 0, 1)
    auth_index: int = int(mark.kwargs.get("auth", 0))

    users: list[CreateUserRequest] = [user_factory() for _ in range(count)]
    if request.node.get_closest_marker("ui"):
        page: Page = request.getfixturevalue("page")
        LoginPage(page).auth_as_user(users[auth_index])


@pytest.fixture(autouse=True)
def admin_session_autologin(
        request: pytest.FixtureRequest,
        admin_user_request: CreateUserRequest
):
    if not request.node.get_closest_marker("admin_session"):
        return
    if request.node.get_closest_marker("ui"):
        page: Page = request.getfixturevalue("page")
        LoginPage(page).auth_as_user(admin_user_request)


@pytest.fixture(autouse=True)
def browser_match_guard(request):
    if request.node.get_closest_marker("api"):
        return

    mark = request.node.get_closest_marker("browsers")
    if not mark:
        return

    allowed = {norm_browser_name(str(x)) for x in (mark.args or ())}
    if not allowed:
        return

    try:
        current = request.getfixturevalue("browser_name")
    except pytest.FixtureLookupError:
        return

    if norm_browser_name(str(current)) not in allowed:
        pytest.skip(f"Пропущен: текущий браузер '{current}' не в {sorted(allowed)}")

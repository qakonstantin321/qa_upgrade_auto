from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Type, TypeVar

from playwright.sync_api import Dialog, Locator, Page

from src.main.api.configs.config import Config
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.specs.request_specs import RequestSpecs

T = TypeVar("T", bound="BasePage")

# Константы для таймаутов
DEFAULT_DIALOG_TIMEOUT = 3000
DEFAULT_PAGE_LOAD_TIMEOUT = 20000
DEFAULT_ELEMENT_TIMEOUT = 10000


class BasePage(ABC):
    def __init__(self, page: Page):
        self.page = page
        self.base_url = str(Config.get("UI_BASE_URL", "http://localhost:3000")).rstrip("/")

    @property
    def username_input(self):
        return self.page.get_by_placeholder("Username")

    @property
    def password_input(self):
        return self.page.get_by_placeholder("Password")

    @abstractmethod
    def url(self) -> str:
        raise NotImplementedError

    def open(self: T) -> T:
        target = self.url()
        if self.base_url and target.startswith("/"):
            target = f"{self.base_url}{target}"
        self.page.goto(target, wait_until="networkidle", timeout=DEFAULT_PAGE_LOAD_TIMEOUT)
        return self

    def get_page(self, page_cls: Type[T]) -> T:
        return page_cls(self.page)

    def check_alert_message_and_accept(self: T, expected_text: str) -> T:
        def _handler(d: Dialog) -> None:
            assert expected_text in d.message, f"Alert text mismatch: {d.message}"
            d.accept()

        self.page.once("dialog", _handler)
        return self

    def auth_as_user(self: T, user_request: CreateUserRequest) -> None:
        auth_token = RequestSpecs.auth_as_user(user_request.username, user_request.password).get("Authorization")
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.goto(self.base_url, timeout=DEFAULT_PAGE_LOAD_TIMEOUT)
        self.page.evaluate('token => localStorage.setItem("authToken", token)', auth_token)

    @staticmethod
    def _generate_page_elements(elements: Locator, constructor: Callable[[Locator], T]) -> Optional[List[T]]:
        count = elements.count()
        if count == 0:
            return []
        elements.first.wait_for(state="attached", timeout=DEFAULT_ELEMENT_TIMEOUT)
        return [constructor(elements.nth(i)) for i in range(elements.count())]

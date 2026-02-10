import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest


@pytest.mark.api
class TestCreateAccount:
    @pytest.mark.check_accounts_change(delta=1)
    def test_create_account(self, api_manager: ApiManager, user_request: CreateUserRequest):
        api_manager.user_steps.create_user_account(user_request)

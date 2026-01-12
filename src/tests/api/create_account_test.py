import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.models.responses.get_transactions_response import GetTransactionsResponse


@pytest.mark.api
class TestCreateAccount:
    def test_create_account(self, api_manager: ApiManager, user_request: CreateUserRequest):
        user_account: CreateAccountResponse = api_manager.user_steps.create_user_account(user_request)

        transactions: GetTransactionsResponse = api_manager.user_steps.get_transactions(user_request, user_account.id)
        assert not transactions

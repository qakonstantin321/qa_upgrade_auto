# pylint: disable=redefined-outer-name
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.classes.session_storage import SessionStorage
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse


@pytest.fixture
def user_request(user_factory):
    try:
        return SessionStorage.get_user(0)
    except IndexError:
        user = user_factory()
        return user


@pytest.fixture
def user_factory(api_manager: ApiManager):
    def create_user() -> CreateUserRequest:
        user_data = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(user_data)
        SessionStorage.add_users([user_data])
        return user_data

    yield create_user


@pytest.fixture
def admin_user_request() -> CreateUserRequest:
    """Возвращение кредов Администратора"""
    return CreateUserRequest(username='admin', password='admin', role='ADMIN')


@pytest.fixture
def create_account(api_manager: ApiManager, user_request: CreateUserRequest) -> CreateAccountResponse:
    """Создание аккаунта"""
    return api_manager.user_steps.create_user_account(user_request=user_request)


@pytest.fixture
def deposit_account(api_manager: ApiManager, user_request: CreateUserRequest,
                    create_account: CreateAccountResponse) -> DepositMoneyResponse:
    """Пополнение аккаунта"""
    return api_manager.user_steps.deposit_money(user_request=user_request, create_account_response=create_account)


@pytest.fixture
def deposit_account_20000_rubbles(api_manager: ApiManager,
                                  user_request: CreateUserRequest,
                                  create_account: CreateAccountResponse) -> DepositMoneyResponse:
    """Пополнение аккаунта на 20000 рублей (4 депозита по 5000)"""
    deposit_money_request: DepositMoneyRequest = RandomModelGenerator.generate(DepositMoneyRequest)
    deposit_money_request.balance = 5000

    previous_response = api_manager.user_steps.deposit_money(
        user_request=user_request,
        create_account_response=create_account,
        deposit_money_request=deposit_money_request
    )

    for _ in range(3):
        previous_response = api_manager.user_steps.deposit_money(
            user_request=user_request,
            create_account_response=create_account,
            deposit_money_request=deposit_money_request,
            previous_response=previous_response
        )

    return previous_response

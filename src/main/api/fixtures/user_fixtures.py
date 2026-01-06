import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.create_user_request import CreateUserRequest


@pytest.fixture(scope='function')
def user_request(api_manager: ApiManager) -> CreateUserRequest:
    user_data: CreateUserRequest = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_data)
    return user_data


@pytest.fixture
def admin_user_request() -> CreateUserRequest:
    return CreateUserRequest(username='admin', password='admin', role='ADMIN')

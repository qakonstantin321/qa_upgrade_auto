import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestCreateUser:
    @pytest.mark.parametrize('create_user_request', [RandomModelGenerator.generate(CreateUserRequest)])
    def test_create_valid_user(self, api_manager: ApiManager, create_user_request: CreateUserRequest):
        api_manager.admin_steps.create_user(create_user_request)

    @pytest.mark.parametrize(
        argnames='username, password, role, error_key, error_value',
        argvalues=[
            ('', RandomData.get_password(), ResponseSpecs.Role.USER.value, 'username',
             ResponseSpecs.USERNAME_CANNOT_BE_BLANK),
            ('ab', RandomData.get_password(), ResponseSpecs.Role.USER.value, 'username',
             ResponseSpecs.USERNAME_LENGTH_INVALID),
            ('qwertyuiopqwerty', RandomData.get_password(), ResponseSpecs.Role.USER.value, 'username',
             ResponseSpecs.USERNAME_LENGTH_INVALID),
            ('@john_doe', RandomData.get_password(), ResponseSpecs.Role.USER.value, 'username',
             ResponseSpecs.USERNAME_INVALID_CHARACTERS),
        ]
    )
    def test_create_invalid_user(self, api_manager: ApiManager,
                                 username: str, password: str, role: str,
                                 error_key: str, error_value: str):
        create_user_req = CreateUserRequest(username=username, password=password, role=role)
        api_manager.admin_steps.create_invalid_user(create_user_req, error_key, error_value)

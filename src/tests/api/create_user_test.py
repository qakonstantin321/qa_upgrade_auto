import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.dao_and_model_assertions import DaoAndModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
@pytest.mark.api_version("with_database")
class TestCreateUser:
    @pytest.mark.check_all_users_change(delta=1, username_source="create_user_request.username", should_exist=True)
    @pytest.mark.parametrize('create_user_request', [RandomModelGenerator.generate(CreateUserRequest)])
    def test_create_valid_user(self, api_manager: ApiManager, create_user_request: CreateUserRequest):
        created = api_manager.admin_steps.create_user(create_user_request)
        user_dao = api_manager.database_steps.get_user_by_username(created.username)
        DaoAndModelAssertions.assert_that(created, user_dao).match()

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
    @pytest.mark.check_all_users_change(delta=0, username_source="username", should_exist=False)
    def test_create_invalid_user(self, api_manager: ApiManager,
                                 username: str, password: str, role: str,
                                 error_key: str, error_value: str):
        create_user_req = CreateUserRequest(username=username, password=password, role=role)
        api_manager.admin_steps.create_invalid_user(create_user_req, error_key, error_value)

        user_dao = api_manager.database_steps.find_user_by_username(username)
        assert user_dao is None, (f"User '{username}' should NOT exist in DB after invalid create, "
                                  f"but was found: {user_dao}")

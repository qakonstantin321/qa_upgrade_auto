import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.update_profile_request import UpdateProfileRequest
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestUpdateProfile:
    def test_valid_update_profile(self, user_request: CreateUserRequest, api_manager: ApiManager):
        api_manager.user_steps.update_profile(user_request)

    @pytest.mark.parametrize(
        argnames='name',
        argvalues=[
            'a ',
            'Петр Иванов',
            '',
            'Will',
            'Will Smith1'
        ]
    )
    def test_invalid_update_profile(self,
                                    user_request: CreateUserRequest,
                                    api_manager: ApiManager,
                                    name: str):
        update_profile_request = UpdateProfileRequest(name=name)
        api_manager.user_steps.invalid_update_profile(
            user_request=user_request,
            update_profile_request=update_profile_request,
            error_value=ResponseSpecs.NAME_INVALID_FORMAT
        )

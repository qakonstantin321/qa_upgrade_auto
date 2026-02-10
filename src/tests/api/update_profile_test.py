import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.update_profile_request import UpdateProfileRequest
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestUpdateProfile:
    @pytest.mark.check_profile_name(expected_before=None, expected_after_source="update_profile_request.name")
    @pytest.mark.parametrize('update_profile_request', [RandomModelGenerator.generate(UpdateProfileRequest)])
    def test_valid_update_profile(self, api_manager: ApiManager,
                                  user_request: CreateUserRequest,
                                  update_profile_request: UpdateProfileRequest):
        api_manager.user_steps.update_profile(user_request, update_profile_request)

    @pytest.mark.check_profile_name(expected_before=None, expected_after=None)
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
    def test_invalid_update_profile(self, api_manager: ApiManager,
                                    user_request: CreateUserRequest, name: str):
        update_profile_req: UpdateProfileRequest = UpdateProfileRequest(name=name)
        api_manager.user_steps.invalid_update_profile(
            user_request=user_request,
            update_profile_request=update_profile_req,
            error_value=ResponseSpecs.NAME_INVALID_FORMAT
        )

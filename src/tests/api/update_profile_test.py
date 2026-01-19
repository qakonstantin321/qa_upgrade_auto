import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.generators.random_data import RandomData
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.update_profile_request import UpdateProfileRequest
from src.main.api.models.responses.get_profile_response import GetProfileResponse
from src.main.api.specs.response_specs import ResponseSpecs


@pytest.mark.api
class TestUpdateProfile:
    def test_valid_update_profile(self, user_request: CreateUserRequest, api_manager: ApiManager):
        get_profile_resp: GetProfileResponse = api_manager.user_steps.get_profile(user_request)
        update_profile_req: UpdateProfileRequest = UpdateProfileRequest(name=RandomData.get_profile_name())
        assert get_profile_resp.name is None

        api_manager.user_steps.update_profile(user_request, update_profile_req)
        get_profile_resp: GetProfileResponse = api_manager.user_steps.get_profile(user_request)
        assert get_profile_resp.name == update_profile_req.name

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
        update_profile_req: UpdateProfileRequest = UpdateProfileRequest(name=name)
        api_manager.user_steps.invalid_update_profile(
            user_request=user_request,
            update_profile_request=update_profile_req,
            error_value=ResponseSpecs.NAME_INVALID_FORMAT
        )

        get_profile_resp: GetProfileResponse = api_manager.user_steps.get_profile(user_request)
        assert get_profile_resp.name is None

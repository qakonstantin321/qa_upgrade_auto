from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.login_user_request import LoginUserRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.steps.base_steps import BaseSteps
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs


class UserSteps(BaseSteps):
    @staticmethod
    def create_account(user_request: CreateUserRequest):
        return CrudRequester(
            RequestSpecs.auth_as_user(
                user_request.username,
                user_request.password
            ),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.entity_was_created()
        ).post(None)

    @staticmethod
    def login(user_request: CreateUserRequest):
        response = CrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_returns_ok()
        ).post(LoginUserRequest(
            username=user_request.username,
            password=user_request.password
        ))
        assert response.headers.get('Authorization')
        return response

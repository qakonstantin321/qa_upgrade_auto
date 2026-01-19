from typing import List, Optional

from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.responses.create_user_response import CreateUserResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class AdminSteps(BaseSteps):
    def create_user(self, user_request: CreateUserRequest) -> CreateUserRequest:
        create_user_response: CreateUserResponse = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.entity_was_created()
        ).post(user_request)
        ModelAssertions(user_request, create_user_response).match()

        self.cleanup_objects.append(create_user_response)

        return user_request

    @staticmethod
    def create_invalid_user(user_request: CreateUserRequest, error_key: str, error_value: str):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_CREATE_USER,
            ResponseSpecs.request_returns_bad_request(error_key, error_value)
        ).post(user_request)

    @staticmethod
    def delete_user(user_id: int):
        CrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_DELETE_USER,
            ResponseSpecs.entity_was_deleted()
        ).delete(user_id)

    @staticmethod
    def get_all_users() -> List[CreateUserResponse]:
        response = ValidatedCrudRequester(
            RequestSpecs.admin_auth_spec(),
            Endpoint.ADMIN_GET_ALL_USERS,
            ResponseSpecs.request_returns_ok()
        ).get()
        return response

    @staticmethod
    def get_user_by_username(user_request: CreateUserRequest) -> Optional[CreateUserResponse]:
        found_user: CreateUserResponse = next(
            (u for u in AdminSteps.get_all_users() if u.username == user_request.username), None)
        return found_user

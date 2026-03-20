import logging
from typing import Dict

import requests

from src.main.api.configs.config import Config
from src.main.api.models.requests.login_user_request import LoginUserRequest
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.specs.response_specs import ResponseSpecs


class RequestSpecs:
    @staticmethod
    def default_req_headers() -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def unauth_spec() -> Dict[str, str]:
        return RequestSpecs.default_req_headers()

    @staticmethod
    def admin_auth_spec() -> Dict[str, str]:
        headers = RequestSpecs.default_req_headers()
        headers["Authorization"] = Config.get("ADMIN_AUTH_HEADER", "Basic YWRtaW46YWRtaW4=")
        return headers

    @staticmethod
    def auth_as_user(username, password) -> Dict[str, str]:
        try:
            response: requests.Response = CrudRequester(
                RequestSpecs.unauth_spec(),
                Endpoint.LOGIN_USER,
                ResponseSpecs.request_returns_ok()
            ).post(LoginUserRequest(username=username, password=password))
        except Exception as exc:
            logging.error("Authentication failed for %s", username)
            raise RuntimeError("Failed to authenticate user") from exc

        auth_header = response.headers.get("Authorization")
        headers = RequestSpecs.default_req_headers()
        headers["Authorization"] = auth_header
        return headers

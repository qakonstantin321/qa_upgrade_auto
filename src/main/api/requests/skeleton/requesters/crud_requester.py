from typing import Optional, TypeVar

import requests

from src.main.api.configs.config import Config
from src.main.api.models.base_model import BaseModel
from src.main.api.requests.skeleton.http_request import HttpRequest
from src.main.api.requests.skeleton.interfaces.crud_end_interface import CrudEndpointInterface

T = TypeVar('T', bound=BaseModel)


class CrudRequester(HttpRequest, CrudEndpointInterface):
    @property
    def base_url(self) -> str:
        return f"{Config.get('server')}{Config.get('apiVersion')}"

    def post(self, model: Optional[T] = None) -> requests.Response:
        body = model.model_dump() if model is not None else ''

        response = requests.post(
            url=f'{self.base_url}{self.endpoint.value.url}',
            headers=self.request_spec,
            json=body,
            timeout=30
        )
        self.response_spec(response)
        return response

    def get(self, _id: Optional[int] = None, **path_params) -> requests.Response:
        url = f'{self.base_url}{self.endpoint.value.url}'
        if path_params:
            url = url.format(**path_params)
        elif _id is not None:
            url = f'{url}/{_id}'

        response = requests.get(
            url=url,
            headers=self.request_spec,
            timeout=30
        )
        self.response_spec(response)
        return response

    def put(self, model: Optional[T] = None) -> requests.Response:
        body = model.model_dump() if model is not None else ''

        response = requests.put(
            url=f'{self.base_url}{self.endpoint.value.url}',
            headers=self.request_spec,
            json=body,
            timeout=30
        )
        self.response_spec(response)
        return response

    def delete(self, _id: int) -> requests.Response:
        response = requests.delete(
            url=f'{self.base_url}{self.endpoint.value.url}/{_id}',
            headers=self.request_spec,
            timeout=30
        )
        self.response_spec(response)
        return response

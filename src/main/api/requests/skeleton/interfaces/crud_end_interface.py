from typing import Optional, Protocol

import requests

from src.main.api.models.base_model import BaseModel


class CrudEndpointInterface(Protocol):
    def post(self, model: BaseModel) -> requests.Response:
        ...

    def get(self, _id: Optional[int] = None) -> requests.Response:
        ...

    def put(self, model: BaseModel) -> requests.Response:
        ...

    def delete(self, _id: int) -> requests.Response:
        ...

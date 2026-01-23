import logging
from typing import Any, Generator, List

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.responses.create_user_response import CreateUserResponse


@pytest.fixture
def created_objects() -> Generator[List[Any], None, None]:
    objects: List[Any] = []
    yield objects

    cleanup_objects(objects)


def cleanup_objects(objects: List[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserResponse):
            api_manager.admin_steps.delete_user(obj.id)
        elif isinstance(obj, CreateUserRequest):
            user_data: CreateUserResponse = api_manager.admin_steps.get_user_by_username(obj)
            if user_data:
                api_manager.admin_steps.delete_user(user_data.id)
        else:
            logging.warning("Object type: %s is not deleted", type(obj))

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
            try:
                user_profile = api_manager.user_steps.get_profile(obj)
            except Exception as e:  # pylint: disable=broad-exception-caught
                username = getattr(obj, "username", obj)
                logging.warning("Skip cleanup for user '%s': %s", username, e)
                continue
            api_manager.admin_steps.delete_user(user_profile.id)
        else:
            logging.warning("Object type: %s is not deleted", type(obj))

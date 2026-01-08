import logging
from typing import Any, Generator, List

import pytest

from src.main.api.classes.api_manager import ApiManager
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
        else:
            logging.warning("Object type: %s is not deleted", type(obj))

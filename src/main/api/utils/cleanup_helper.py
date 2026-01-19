import logging
from typing import Any, List

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.responses.create_user_response import CreateUserResponse


def cleanup_objects(objects: List[Any]):
    api_manager = ApiManager(objects)
    for obj in objects:
        if isinstance(obj, CreateUserRequest):
            user_profile = api_manager.user_steps.get_profile(obj)
            api_manager.admin_steps.delete_user(user_profile.id)
        if isinstance(obj, CreateUserResponse):
            api_manager.admin_steps.delete_user(obj.id)
        else:
            logging.warning('Object type: %s is not deleted', type(obj))

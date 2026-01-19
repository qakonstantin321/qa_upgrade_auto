from typing import List

from src.main.api.models.requests.create_user_request import CreateUserRequest


class SessionStorage:
    _users: List[CreateUserRequest] = []

    @classmethod
    def add_users(cls, users: List[CreateUserRequest]) -> None:
        for user in list(users):
            cls._users.append(user)

    @classmethod
    def get_user(cls, index: int = 0) -> CreateUserRequest:
        if index >= len(cls._users):
            raise IndexError(
                f"User index (0-based) out of range: {index}; total={len(cls._users)}"
            )
        return cls._users[index]

    @classmethod
    def clear(cls) -> None:
        cls._users.clear()

from enum import Enum
from http import HTTPStatus
from typing import Callable, Optional

from requests import Response


class ResponseSpecs:
    class TransactionType(str, Enum):
        DEPOSIT = "DEPOSIT"
        TRANSFER_OUT = "TRANSFER_OUT"
        TRANSFER_IN = "TRANSFER_IN"

    class Role(str, Enum):
        USER = "USER"
        ADMIN = "ADMIN"

    # Username validation
    USERNAME_CANNOT_BE_BLANK = "Username cannot be blank"
    USERNAME_LENGTH_INVALID = "Username must be between 3 and 15 characters"
    USERNAME_INVALID_CHARACTERS = "Username must contain only letters, digits, dashes, underscores, and dots"

    # Deposit validation
    DEPOSIT_MIN_AMOUNT = "Invalid account or amount"
    DEPOSIT_MAX_AMOUNT = "Deposit amount exceeds the 5000 limit"

    # Transfer validation
    TRANSFER_MIN_AMOUNT = "Invalid transfer: insufficient funds or invalid accounts"
    TRANSFER_MAX_AMOUNT = "Transfer amount cannot exceed 10000"

    # Profile validation
    NAME_INVALID_FORMAT = "Name must contain two words with letters only"

    @staticmethod
    def _make_status_checker(expected_statuses: list[HTTPStatus]) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code in expected_statuses, (
                f"Expected status {expected_statuses}, but got {response.status_code}. "
                f"Response body: {response.text}"
            )

        return check

    @staticmethod
    def request_returns_ok() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK])

    @staticmethod
    def entity_was_created() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.CREATED])

    @staticmethod
    def entity_was_deleted() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.OK, HTTPStatus.NO_CONTENT])

    @staticmethod
    def entity_was_forbidden() -> Callable[[Response], None]:
        return ResponseSpecs._make_status_checker([HTTPStatus.FORBIDDEN])

    @staticmethod
    def request_returns_bad_request(
            error_key: Optional[str] = None,
            error_value: Optional[str] = None
    ) -> Callable[[Response], None]:
        def check(response: Response):
            assert response.status_code == HTTPStatus.BAD_REQUEST, (
                f"Expected 400 BAD_REQUEST, got {response.status_code}. Response: {response.text}"
            )
            if error_key:
                actual_value = response.json().get(error_key)
            else:
                actual_value = response.text
            assert error_value in actual_value, (
                f"Expected error field '{error_key}' to be '{error_value}', but got '{actual_value}'."
            )

        return check

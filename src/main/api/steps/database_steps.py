from __future__ import annotations

from typing import Optional, Union

from src.main.api.database.dao.account_dao import AccountDao
from src.main.api.database.dao.transaction_dao import TransactionDao
from src.main.api.database.dao.user_dao import UserDao
from src.main.api.database.db_client import Condition, DBRequest, RequestType


class DataBaseSteps:
    @staticmethod
    def get_user_by_username(username: str) -> UserDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("username", username))
            .extract_as(UserDao)
        )

    @staticmethod
    def find_user_by_username(username: str) -> Optional[UserDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("customers")
            .where(Condition.equal_to("username", username))
            .extract_optional_as(UserDao)
        )

    @staticmethod
    def get_account_by_account_number(account_number: str) -> AccountDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("accounts")
            .where(Condition.equal_to("account_number", account_number))
            .extract_as(AccountDao)
        )

    @staticmethod
    def find_account_by_account_number(account_number: str) -> Optional[AccountDao]:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("accounts")
            .where(Condition.equal_to("account_number", account_number))
            .extract_optional_as(AccountDao)
        )

    @staticmethod
    def get_transaction_by_account_id(account_id: Union[str, int], index: int = 0) -> TransactionDao:
        builder = (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("transactions")
            .where(Condition.equal_to("account_id", str(account_id)))
        )
        if index >= 0:
            builder = builder.offset(index)
        elif index == -1:
            builder = builder.order_by("id", descending=True)

        return builder.extract_as(TransactionDao)

    @staticmethod
    def find_transaction_by_account_id(account_id: Union[str, int]) -> TransactionDao:
        return (
            DBRequest.builder()
            .request_type(RequestType.SELECT)
            .table("transactions")
            .where(Condition.equal_to("account_id", str(account_id)))
            .extract_optional_as(TransactionDao)
        )

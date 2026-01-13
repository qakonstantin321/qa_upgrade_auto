from typing import Optional

from src.main.api.generators.random_model_generator import RandomModelGenerator
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.requests.deposit_money_request import DepositMoneyRequest
from src.main.api.models.requests.login_user_request import LoginUserRequest
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.requests.update_profile_request import UpdateProfileRequest
from src.main.api.models.responses.create_account_response import CreateAccountResponse
from src.main.api.models.responses.deposit_money_response import DepositMoneyResponse
from src.main.api.models.responses.get_profile_response import GetProfileResponse
from src.main.api.models.responses.get_transactions_response import GetTransactionsResponse
from src.main.api.models.responses.login_user_response import LoginUserResponse
from src.main.api.models.responses.transfer_money_response import TransferMoneyResponse
from src.main.api.models.responses.update_profile_response import UpdateProfileResponse
from src.main.api.requests.skeleton.endpoint import Endpoint
from src.main.api.requests.skeleton.requesters.crud_requester import CrudRequester
from src.main.api.requests.skeleton.requesters.validated_crud_requester import ValidatedCrudRequester
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    @staticmethod
    def login(user_request: CreateUserRequest) -> LoginUserResponse:
        login_request = LoginUserRequest(username=user_request.username, password=user_request.password)
        login_response: LoginUserResponse = ValidatedCrudRequester(
            RequestSpecs.unauth_spec(),
            Endpoint.LOGIN_USER,
            ResponseSpecs.request_returns_ok()
        ).post(login_request)
        ModelAssertions(login_request, login_response).match()
        return login_response

    @staticmethod
    def create_user_account(user_request: CreateUserRequest) -> CreateAccountResponse:
        create_account_response: CreateAccountResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.entity_was_created()
        ).post()

        assert create_account_response.balance == 0.0
        assert not create_account_response.transactions
        return create_account_response

    @staticmethod
    def deposit_money(user_request: CreateUserRequest,
                      create_account_response: CreateAccountResponse,
                      deposit_money_request: DepositMoneyRequest = RandomModelGenerator.generate(DepositMoneyRequest),
                      previous_response: Optional[DepositMoneyResponse] = None
                      ) -> DepositMoneyResponse:
        deposit_money_request.id = create_account_response.id
        current_balance = previous_response.balance if previous_response else create_account_response.balance

        deposit_money_response: DepositMoneyResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.DEPOSIT_MONEY,
            ResponseSpecs.request_returns_ok()
        ).post(deposit_money_request)

        expected_balance = current_balance + deposit_money_request.balance
        assert deposit_money_response.balance == expected_balance
        assert create_account_response.accountNumber == deposit_money_response.accountNumber
        assert deposit_money_response.transactions
        return deposit_money_response

    @staticmethod
    def get_transactions(user_request: CreateUserRequest,
                         account_id: int) -> GetTransactionsResponse:
        return ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_TRANSACTIONS,
            ResponseSpecs.request_returns_ok()
        ).get(accountId=account_id)

    @staticmethod
    def get_transactions_forbidden(user_request: CreateUserRequest,
                                   account_id: int):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_TRANSACTIONS,
            ResponseSpecs.entity_was_forbidden()
        ).get(accountId=account_id)

    @staticmethod
    def invalid_deposit_money(user_request: CreateUserRequest,
                              deposit_money_request: DepositMoneyRequest,
                              error_value: str):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.DEPOSIT_MONEY,
            ResponseSpecs.request_returns_bad_request(error_value=error_value)
        ).post(deposit_money_request)

    @staticmethod
    def deposit_money_invalid_account(user_request: CreateUserRequest,
                                      deposit_money_request: DepositMoneyRequest):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.DEPOSIT_MONEY,
            ResponseSpecs.entity_was_forbidden()
        ).post(deposit_money_request)

    @staticmethod
    def transfer_money(user_request: CreateUserRequest,
                       transfer_money_request: TransferMoneyRequest
                       ) -> TransferMoneyResponse:
        transfer_money_response: TransferMoneyResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER_MONEY,
            ResponseSpecs.request_returns_ok()
        ).post(transfer_money_request)

        assert transfer_money_request.amount == transfer_money_response.amount
        assert transfer_money_request.senderAccountId == transfer_money_response.senderAccountId
        assert transfer_money_request.receiverAccountId == transfer_money_response.receiverAccountId
        assert transfer_money_response.message == 'Transfer successful'
        return transfer_money_response

    @staticmethod
    def invalid_transfer_money(user_request: CreateUserRequest,
                               transfer_money_request: TransferMoneyRequest,
                               error_value: str):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.TRANSFER_MONEY,
            ResponseSpecs.request_returns_bad_request(error_value=error_value)
        ).post(transfer_money_request)

    @staticmethod
    def get_profile(user_request: CreateUserRequest) -> GetProfileResponse:
        return ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.GET_PROFILE,
            ResponseSpecs.request_returns_ok()
        ).get()

    @staticmethod
    def update_profile(user_request: CreateUserRequest,
                       update_profile_request: UpdateProfileRequest = RandomModelGenerator.generate(
                           UpdateProfileRequest)
                       ) -> UpdateProfileResponse:
        update_profile_response: UpdateProfileResponse = ValidatedCrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.UPDATE_PROFILE,
            ResponseSpecs.request_returns_ok()
        ).put(update_profile_request)

        assert update_profile_response.customer.name == update_profile_request.name
        assert update_profile_response.message == "Profile updated successfully"
        return update_profile_response

    @staticmethod
    def invalid_update_profile(user_request: CreateUserRequest,
                               update_profile_request: UpdateProfileRequest,
                               error_value: str):
        CrudRequester(
            RequestSpecs.auth_as_user(user_request.username, user_request.password),
            Endpoint.UPDATE_PROFILE,
            ResponseSpecs.request_returns_bad_request(error_value=error_value)
        ).put(update_profile_request)

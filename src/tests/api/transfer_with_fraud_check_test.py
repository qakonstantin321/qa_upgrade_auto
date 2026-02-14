import random

import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.responses.transfer_money_response import TransferMoneyResponse

FRAUD_APPROVED_MOCK = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.2,
    "reason": "Low risk transaction",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

FRAUD_APPROVED_EXPECTED = {
    "fraudRiskScore": FRAUD_APPROVED_MOCK["riskScore"],
    "fraudReason": FRAUD_APPROVED_MOCK["reason"],
    "requiresManualReview": False,
    "requiresVerification": False,
}

TRANSFER_APPROVED_EXPECTED = {
    "status": "APPROVED",
    "message": "Transfer approved and processed immediately",
    **FRAUD_APPROVED_EXPECTED,
}


@pytest.mark.api
@pytest.mark.api_version("with_fraud_check")
@pytest.mark.prepare_users(number=2)
@pytest.mark.prepare_accounts(number=2, deposit=5000)
class TestTransferWithFraudCheck:
    @pytest.mark.fraud_check_mock(
        port=8080,
        endpoint=r"/.*",
        **FRAUD_APPROVED_MOCK,
    )
    def test_transfer_with_fraud_check(
            self,
            api_manager: ApiManager,
            prepared_user_accounts: list[PreparedUserAccount],
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]

        with allure.step("Transfer with fraud check"):
            transfer_amount = round(random.uniform(0.1, 4999.9), 2)
            transfer_request = TransferMoneyRequest(
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                amount=transfer_amount,
            )
            transfer_response = api_manager.user_steps.transfer_with_fraud_check(
                sender.user,
                transfer_request,
            )

        with allure.step("Validate transfer response matches mocked fraud decision"):
            expected = TransferMoneyResponse(
                amount=transfer_amount,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                **TRANSFER_APPROVED_EXPECTED,
            )
            ModelAssertions(expected, transfer_response).match()

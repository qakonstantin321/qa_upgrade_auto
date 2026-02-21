import random

import allure
import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.fixtures.prepare_data_fixtures import PreparedUserAccount
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.transfer_money_request import TransferMoneyRequest
from src.main.api.models.responses.transfer_money_response import TransferMoneyResponse


def _build_fraud_expected(mock: dict) -> dict:
    """Build expected fraud fields from mock response."""
    return {
        "fraudRiskScore": mock["riskScore"],
        "fraudReason": mock["reason"],
        "requiresManualReview": mock["requiresManualReview"],
        "requiresVerification": mock["additionalVerificationRequired"],
    }


FRAUD_APPROVED_MOCK = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.2,
    "reason": "Low risk transaction",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

TRANSFER_APPROVED_EXPECTED = {
    "status": "APPROVED",
    "message": "Transfer approved and processed immediately",
    **_build_fraud_expected(FRAUD_APPROVED_MOCK),
}

TRANSFER_CHECK_STATUS_EXPECTED = {
    "status": "NO_FRAUD_CHECK_REQUIRED",
    "note": "This transaction does not require fraud checking.",
}

MANUAL_REVIEW_BASE = {
    "status": "MANUAL_REVIEW_REQUIRED",
    "message": "Transfer requires manual review",
}

FRAUD_MANUAL_MOCK = {
    "status": "INVALID_STATUS",
    "decision": "APPROVED",
    "riskScore": 0.2,
    "reason": "Manual review required from provider",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

TRANSFER_MANUAL_REVIEW_EXPECTED = {
    **MANUAL_REVIEW_BASE,
    **_build_fraud_expected(FRAUD_MANUAL_MOCK),
}

FRAUD_REJECTED_MOCK = {
    "status": "SUCCESS",
    "decision": "REJECTED",
    "riskScore": 0.95,
    "reason": "High risk transaction detected",
    "requiresManualReview": False,
    "additionalVerificationRequired": False,
}

TRANSFER_REJECTED_EXPECTED = {
    **MANUAL_REVIEW_BASE,
    **_build_fraud_expected(FRAUD_REJECTED_MOCK),
}

FRAUD_HIGH_RISK_MOCK = {
    "status": "SUCCESS",
    "decision": "APPROVED",
    "riskScore": 0.85,
    "reason": "Suspicious transaction pattern",
    "requiresManualReview": True,
    "additionalVerificationRequired": False,
}

TRANSFER_HIGH_RISK_EXPECTED = {
    **MANUAL_REVIEW_BASE,
    **_build_fraud_expected(FRAUD_HIGH_RISK_MOCK),
}

USER_SOURCE = "fraud_check_user"
ACCOUNT_ID_SOURCE = "fraud_check_account_id"
APPROVED = "approved"
MANUAL_REVIEW = "manual_review"
REJECTED = "rejected"
HIGH_RISK = "high_risk"

STEP_DESCRIPTIONS = {
    MANUAL_REVIEW: "Transfer with fraud check (manual review required from mock)",
    REJECTED: "Transfer with fraud check (rejected by fraud service)",
    HIGH_RISK: "Transfer with fraud check (high risk, requires manual review)",
}

VALIDATION_STEPS = {
    MANUAL_REVIEW: "Validate transfer response requires manual review",
    REJECTED: "Validate transfer response is rejected",
    HIGH_RISK: "Validate transfer response has high risk flags",
}


@pytest.mark.api
@pytest.mark.api_version("with_fraud_check")
@pytest.mark.prepare_users(number=2)
@pytest.mark.prepare_accounts(number=2, deposit=5000)
@pytest.mark.xdist_group(name="Fraud")
class TestTransferWithFraudCheck:
    """Test suite for transfer money with fraud check integration.

    Covers different fraud detection scenarios:
    - APPROVED: Low risk transaction, approved immediately
    - MANUAL_REVIEW: Invalid status from fraud provider, requires manual review
    - REJECTED: High risk transaction rejected by fraud service
    - HIGH_RISK: Suspicious pattern detected, requires manual review
    """

    @pytest.mark.parametrize(
        "expected_transfer_response,test_description",
        [
            pytest.param(
                TRANSFER_APPROVED_EXPECTED,
                APPROVED,
                marks=[
                    pytest.mark.fraud_check_mock(port=8080, endpoint=r"/.*", **FRAUD_APPROVED_MOCK),
                    pytest.mark.check_fraud_status(
                        user_source=USER_SOURCE,
                        account_id_source=ACCOUNT_ID_SOURCE,
                        expected_dict=TRANSFER_CHECK_STATUS_EXPECTED,
                    ),
                ],
                id=APPROVED,
            ),
            pytest.param(
                TRANSFER_MANUAL_REVIEW_EXPECTED,
                MANUAL_REVIEW,
                marks=[
                    pytest.mark.fraud_check_mock(port=8080, endpoint=r"/.*", **FRAUD_MANUAL_MOCK),
                ],
                id=MANUAL_REVIEW,
            ),
            pytest.param(
                TRANSFER_REJECTED_EXPECTED,
                REJECTED,
                marks=[
                    pytest.mark.fraud_check_mock(port=8080, endpoint=r"/.*", **FRAUD_REJECTED_MOCK),
                ],
                id=REJECTED,
            ),
            pytest.param(
                TRANSFER_HIGH_RISK_EXPECTED,
                HIGH_RISK,
                marks=[
                    pytest.mark.fraud_check_mock(port=8080, endpoint=r"/.*", **FRAUD_HIGH_RISK_MOCK),
                ],
                id=HIGH_RISK,
            ),
        ],
    )
    def test_transfer_with_fraud_check(
            self,
            api_manager: ApiManager,
            prepared_user_accounts: list[PreparedUserAccount],
            request: pytest.FixtureRequest,
            expected_transfer_response: dict,
            test_description: str,
    ):
        with allure.step("Prepare sender/receiver accounts (2 accounts with deposit=5000)"):
            sender = prepared_user_accounts[0]
            receiver = prepared_user_accounts[1]

        # Save user/account for fraud status check fixture
        request.node.user_properties[USER_SOURCE] = sender.user
        request.node.user_properties[ACCOUNT_ID_SOURCE] = sender.account

        step_description = STEP_DESCRIPTIONS.get(test_description, "Transfer with fraud check")
        with allure.step(step_description):
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

        validation_step = VALIDATION_STEPS.get(
            test_description,
            "Validate transfer response matches mocked fraud decision"
        )
        with allure.step(validation_step):
            expected = TransferMoneyResponse(
                amount=transfer_amount,
                senderAccountId=sender.account.id,
                receiverAccountId=receiver.account.id,
                **expected_transfer_response,
            )
            ModelAssertions(expected, transfer_response).match()

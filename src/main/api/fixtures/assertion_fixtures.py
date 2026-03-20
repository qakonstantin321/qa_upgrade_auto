from typing import Any, Optional

import pytest

from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.comparison.model_assertions import ModelAssertions
from src.main.api.models.requests.create_user_request import CreateUserRequest
from src.main.api.models.responses.fraud_check_status_response import FraudCheckStatusResponse
from src.main.api.specs.response_specs import ResponseSpecs


def _resolve_source(request: pytest.FixtureRequest, source: str) -> Any:
    """
    Resolve "fixture_or_param.attr1.attr2" into a concrete value.
    Examples:
      - "username" -> request.getfixturevalue("username")
      - "create_user_request.username" -> request.getfixturevalue("create_user_request").username
    """
    parts = [p for p in source.split(".") if p]
    if not parts:
        raise ValueError("username_source is empty")

    root = parts[0]

    # Parametrized values live in callspec.params (not always accessible via getfixturevalue on teardown).
    callspec = getattr(request.node, "callspec", None)
    if callspec is not None and root in getattr(callspec, "params", {}):
        value = callspec.params[root]
    else:
        # Fixture values
        value = request.getfixturevalue(root)

    for attr in parts[1:]:
        value = getattr(value, attr)
    return value


@pytest.fixture(autouse=True)
def init_user_properties(request: pytest.FixtureRequest):
    """Initialize user_properties dict on request.node to avoid repeated checks in tests."""
    if not isinstance(request.node.user_properties, dict):
        request.node.user_properties = {}


@pytest.fixture(autouse=True)
def entity_will_be_created(request: pytest.FixtureRequest):
    """
    Marker-driven helper for cleanup: adds entity/entities to `created_objects`.

    Use in UI tests where creation happens via UI (not via API steps), so the cleanup list
    wouldn't be populated automatically.

    Examples:
      @pytest.mark.entity_will_be_created("new_user_request")
      @pytest.mark.entity_will_be_created("some_fixture.attr")
    """
    mark = request.node.get_closest_marker("entity_will_be_created")
    if not mark:
        yield
        return

    api_manager: ApiManager = request.getfixturevalue("api_manager")

    sources = list(mark.args or [])
    source_kw = mark.kwargs.get("source")
    if source_kw:
        sources.append(source_kw)

    if not sources:
        raise ValueError("entity_will_be_created requires at least one source (e.g. 'new_user_request')")

    for src in sources:
        entity = _resolve_source(request, str(src)) if isinstance(src, str) else src
        api_manager.admin_steps.cleanup_objects.append(entity)

    yield


@pytest.fixture(autouse=True)
def check_all_users_change(request: pytest.FixtureRequest):
    """
    Marker-driven post-action verification for API tests.

    Usage:
      @pytest.mark.check_all_users_change(delta=1, username_source="create_user_request.username")
      @pytest.mark.check_all_users_change(delta=0, username_source="username")
    """
    mark = request.node.get_closest_marker("check_all_users_change")
    if not mark:
        yield
        return

    delta = int(mark.kwargs.get("delta", 0))
    username_source: Optional[str] = mark.kwargs.get("username_source")
    should_exist = mark.kwargs.get("should_exist")
    if should_exist is None:
        should_exist = delta > 0
    should_exist = bool(should_exist)

    # In xdist (or other parallel runs) global "count delta" is not stable, because other tests
    # can create/delete users between our before/after snapshots. Allow opting into strict mode.
    strict_delta = bool(mark.kwargs.get("strict_delta", False))
    running_xdist = hasattr(request.config, "workerinput")

    api_manager: ApiManager = request.getfixturevalue("api_manager")

    # Resolve username early (before yield), while parametrized args are still accessible.
    resolved_username: Optional[str] = None
    if username_source:
        resolved_username = str(_resolve_source(request, username_source))

    before = api_manager.admin_steps.get_all_users()
    before_usernames = {u.username for u in before}
    yield
    after = api_manager.admin_steps.get_all_users()
    after_usernames = {u.username for u in after}

    if resolved_username is not None:
        if should_exist:
            assert resolved_username in after_usernames, (
                f"Expected user '{resolved_username}' existence=True via GET /admin/users, "
                f"but it was not found."
            )
            # In sequential runs we can also assert the user wasn't present before (true "creation").
            if (not running_xdist) and delta > 0:
                assert resolved_username not in before_usernames, (
                    f"Expected user '{resolved_username}' to be newly created, but it already existed before."
                )
        else:
            assert resolved_username not in after_usernames, (
                f"Expected user '{resolved_username}' existence=False via GET /admin/users, "
                f"but it was found."
            )

    # Count delta is reliable only in sequential runs (or when explicitly requested).
    if strict_delta and not running_xdist:
        assert len(after) - len(before) == delta, (
            f"Expected users delta={delta} (after-before), but got {len(after) - len(before)}. "
            f"before={len(before)}, after={len(after)}"
        )


@pytest.fixture(autouse=True)
def check_accounts_change(request: pytest.FixtureRequest):
    """
    Marker-driven post-action verification for accounts (customer accounts list).

    Usage:
      @pytest.mark.check_accounts_change(delta=1)
    """
    mark = request.node.get_closest_marker("check_accounts_change")
    if not mark:
        yield
        return

    delta = int(mark.kwargs.get("delta", 0))

    # UI tests: ensure @pytest.mark.user_session(...) autouse hook ran BEFORE we snapshot accounts.
    # Otherwise SessionStorage may be empty/cleared and `user_request` may refer to a different user
    # than the one logged-in in UI, causing false delta=0.
    if request.node.get_closest_marker("user_session") is not None:
        try:
            request.getfixturevalue("user_session_extension")
        except pytest.FixtureLookupError:
            # In non-UI contexts this fixture may not exist; ignore.
            pass

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = request.getfixturevalue("user_request")

    before = api_manager.user_steps.get_all_accounts(user_request)

    yield

    after = api_manager.user_steps.get_all_accounts(user_request)

    assert len(after) - len(before) == delta, (
        f"Expected accounts delta={delta} (after-before), but got {len(after) - len(before)}. "
        f"before={len(before)}, after={len(after)}"
    )


@pytest.fixture(autouse=True)
def check_transactions_count(request: pytest.FixtureRequest):
    """
    Marker-driven verification for transactions count.

    Usage:
      @pytest.mark.check_transactions_count(account_id_source="create_account.id", expected_before=0, expected_after=1)
      @pytest.mark.check_transactions_count(account_id_source="create_account.id", expected_after=0)
    """
    mark = request.node.get_closest_marker("check_transactions_count")
    if not mark:
        yield
        return

    account_id_source: str = mark.kwargs.get("account_id_source")
    expected_before: Optional[int] = mark.kwargs.get("expected_before")
    expected_after: Optional[int] = mark.kwargs.get("expected_after")

    if not account_id_source:
        raise ValueError("check_transactions_count requires account_id_source")

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = request.getfixturevalue("user_request")

    account_id = int(_resolve_source(request, account_id_source))

    before_count = None
    if expected_before is not None:
        before_resp = api_manager.user_steps.get_transactions(user_request, account_id)
        before_count = len(before_resp.transactions)
        assert before_count == expected_before, (
            f"Expected {expected_before} transactions before, but got {before_count}"
        )

    yield

    if expected_after is not None:
        after_resp = api_manager.user_steps.get_transactions(user_request, account_id)
        after_count = len(after_resp.transactions)
        assert after_count == expected_after, (
            f"Expected {expected_after} transactions after, but got {after_count}"
        )


@pytest.fixture(autouse=True)
def check_deposit_transaction_match(request: pytest.FixtureRequest):
    """
    Marker-driven verification that deposit transaction matches get_transactions response.
    Requires deposit_money_response to be stored in request.node.deposit_money_response.

    Usage:
      @pytest.mark.check_deposit_transaction_match(account_id_source="create_account.id")
    """
    mark = request.node.get_closest_marker("check_deposit_transaction_match")
    if not mark:
        yield
        return

    account_id_source: str = mark.kwargs.get("account_id_source")

    if not account_id_source:
        raise ValueError("check_deposit_transaction_match requires account_id_source")

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = request.getfixturevalue("user_request")

    # Resolve account_id early (before yield), while fixtures are still available
    account_id = int(_resolve_source(request, account_id_source))

    yield

    get_transactions_resp = api_manager.user_steps.get_transactions(user_request, account_id)
    # Get deposit_money_response from node user_properties (guaranteed to exist by init_user_properties)
    user_props = request.node.user_properties
    deposit_response = user_props.get('deposit_money_response')
    if deposit_response and deposit_response.transactions and len(deposit_response.transactions) > 0:
        assert len(get_transactions_resp.transactions) == 1, (
            f"Expected 1 transaction, but got {len(get_transactions_resp.transactions)}"
        )
        ModelAssertions(deposit_response.transactions[0], get_transactions_resp.transactions[0]).match()
    else:
        assert len(get_transactions_resp.transactions) == 1, (
            f"Expected 1 transaction, but got {len(get_transactions_resp.transactions)}"
        )


@pytest.fixture(autouse=True)
def check_transfer_transaction(request: pytest.FixtureRequest):
    """
    Marker-driven verification for transfer transaction.

    Usage:
      @pytest.mark.check_transfer_transaction(
          receiver_user_source="user_2",
          receiver_account_id_source="account_user_2.id",
          sender_account_id_source="deposit_account.id"
      )
    """
    mark = request.node.get_closest_marker("check_transfer_transaction")
    if not mark:
        yield
        return

    receiver_user_source: str = mark.kwargs.get("receiver_user_source")
    receiver_account_id_source: str = mark.kwargs.get("receiver_account_id_source")
    sender_account_id_source: Optional[str] = mark.kwargs.get("sender_account_id_source")

    if not receiver_user_source or not receiver_account_id_source:
        raise ValueError("check_transfer_transaction requires receiver_user_source and receiver_account_id_source")

    api_manager: ApiManager = request.getfixturevalue("api_manager")

    # Resolve sender_account_id early (before yield), while fixtures are still available
    sender_account_id: Optional[int] = None
    if sender_account_id_source:
        sender_account_id = int(_resolve_source(request, sender_account_id_source))

    yield

    # Resolve receiver_user and receiver_account_id
    # First try user_properties (for dynamically created objects in tests)
    user_props = request.node.user_properties
    receiver_user = user_props.get(receiver_user_source)
    if not receiver_user:
        receiver_user = _resolve_source(request, receiver_user_source)
    account_obj_name = receiver_account_id_source.split('.')[0]
    receiver_account_obj = user_props.get(account_obj_name)
    if receiver_account_obj:
        receiver_account_id = int(getattr(receiver_account_obj, receiver_account_id_source.split('.')[-1]))
    else:
        receiver_account_id = int(_resolve_source(request, receiver_account_id_source))

    get_transactions_resp = api_manager.user_steps.get_transactions(receiver_user, receiver_account_id)
    assert len(get_transactions_resp.transactions) == 1, (
        f"Expected 1 transaction, but got {len(get_transactions_resp.transactions)}"
    )

    tr = get_transactions_resp.transactions[-1]
    assert tr.type == ResponseSpecs.TransactionType.TRANSFER_IN.value
    if sender_account_id is not None:
        assert tr.relatedAccountId == sender_account_id
    transfer_response = user_props.get('transfer_response')
    if transfer_response:
        assert tr.amount == transfer_response.amount
        assert tr.relatedAccountId == transfer_response.senderAccountId


@pytest.fixture(autouse=True)
def check_fraud_status(request: pytest.FixtureRequest):
    """
    Marker-driven verification for fraud-check status by transaction ID.

    Usage (example):
      @pytest.mark.check_fraud_status(
          user_source="fraud_check_user",
          account_id_source="fraud_check_account_id",
          expected_dict=TRANSFER_CHECK_STATUS_APPROVED_EXPECTED,
      )
    """
    mark = request.node.get_closest_marker("check_fraud_status")
    if not mark:
        yield
        return

    user_source: str = mark.kwargs.get("user_source")
    account_id_source: str = mark.kwargs.get("account_id_source")
    expected_dict: dict = mark.kwargs.get("expected_dict")

    if not user_source or not account_id_source:
        raise ValueError("check_fraud_status requires user_source and account_id_source")
    if not expected_dict:
        raise ValueError("check_fraud_status requires expected_dict")

    api_manager: ApiManager = request.getfixturevalue("api_manager")

    yield

    user_props = request.node.user_properties

    user = user_props.get(user_source)
    if not user:
        user = _resolve_source(request, user_source)

    account_parts = account_id_source.split('.')
    account_obj_name = account_parts[0]
    account_attr_name = account_parts[1] if len(account_parts) > 1 else "id"

    account_obj = user_props.get(account_obj_name)
    if account_obj:
        account_id = int(getattr(account_obj, account_attr_name))
    else:
        account_id = int(_resolve_source(request, account_id_source))

    get_transactions_resp = api_manager.user_steps.get_transactions(user, account_id)
    assert len(get_transactions_resp.transactions) > 0, (
        f"Expected at least 1 transaction, but got {len(get_transactions_resp.transactions)}"
    )

    transaction_id = get_transactions_resp.transactions[-1].id

    fraud_check_resp = api_manager.user_steps.check_fraud_status(user, transaction_id)

    expected_model = FraudCheckStatusResponse(
        **expected_dict,
        transactionId=transaction_id,
    )
    ModelAssertions(expected_model, fraud_check_resp).match()


@pytest.fixture(autouse=True)
def check_profile_name(request: pytest.FixtureRequest):
    """
    Marker-driven verification for profile name.

    Usage:
      @pytest.mark.check_profile_name(expected_before=None, expected_after_source="update_profile_request.name")
      @pytest.mark.check_profile_name(expected_before=None, expected_after=None)
    """
    mark = request.node.get_closest_marker("check_profile_name")
    if not mark:
        yield
        return

    expected_before: Optional[str] = mark.kwargs.get("expected_before")
    expected_after_source: Optional[str] = mark.kwargs.get("expected_after_source")
    expected_after: Optional[str] = mark.kwargs.get("expected_after")

    api_manager: ApiManager = request.getfixturevalue("api_manager")
    user_request: CreateUserRequest = request.getfixturevalue("user_request")

    # Resolve expected_after_value early (before yield), while fixtures/params are still available
    expected_after_value: Optional[str] = None
    if expected_after_source:
        expected_after_value = str(_resolve_source(request, expected_after_source))
    elif expected_after is not None:
        expected_after_value = expected_after

    if expected_before is not None:
        before_profile = api_manager.user_steps.get_profile(user_request)
        assert before_profile.name == expected_before, (
            f"Expected profile name before to be {expected_before}, but got {before_profile.name}"
        )

    yield

    after_profile = api_manager.user_steps.get_profile(user_request)
    if expected_after_value is not None:
        assert after_profile.name == expected_after_value, (
            f"Expected profile name after to be {expected_after_value}, but got {after_profile.name}"
        )

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Union

from src.main.api.specs.response_specs import ResponseSpecs


@dataclass
class TransactionDao:
    """
    Representation of a row in 'transactions' table.
    Field names are expected to match DB columns (snake_case).
    """

    id: int
    amount: Union[int, float]
    type: ResponseSpecs.TransactionType
    timestamp: datetime
    account_id: int
    related_account_id: int
    created_at: datetime

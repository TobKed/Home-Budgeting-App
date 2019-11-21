"""Module with Expenditure class."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Expenditure:
    """Class which defines basic expenditure."""

    value: float
    date: datetime
    category: str
    comment: Optional[str]

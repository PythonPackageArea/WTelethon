"""Response модели для TData helpers."""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class TDataAccount:
    """Модель аккаунта в TData."""

    index: int
    dc: Optional[int] = None
    error: bool = False


@dataclass
class TDataInfo:
    """Модель информации о TData."""

    accounts_count: int
    accounts: List[TDataAccount]
    has_passcode: bool
    sessions: List[str]

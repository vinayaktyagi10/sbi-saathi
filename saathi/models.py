"""Core data structures for SBI Saathi.

Kept as plain dataclasses so the MVP runs with zero external dependencies and
the logic stays readable for hackathon judges reviewing the repo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Action(str, Enum):
    ALLOW = "ALLOW"                 # proceed silently
    SOFT_WARN = "SOFT_WARN"         # proceed but inform
    HARD_CONFIRM = "HARD_CONFIRM"   # pause, explain, require explicit re-confirmation
    BLOCK = "BLOCK"                 # block and explain; needs a cooling-off / human check


@dataclass
class User:
    user_id: str
    name: str
    language: str = "en"            # en, hi, ta, ... (ISO-ish codes)
    balance: float = 0.0
    is_first_time_digital: bool = False
    # Historical behaviour the fraud engine reasons over
    avg_txn_amount: float = 0.0
    max_txn_amount: float = 0.0
    known_payees: list[str] = field(default_factory=list)


@dataclass
class Payee:
    name: str
    upi_id: str
    added_at: datetime
    in_contacts: bool = False


@dataclass
class Transaction:
    user_id: str
    amount: float
    payee: Payee
    initiated_at: datetime = field(default_factory=datetime.now)
    # Contextual signals captured from the session / device
    message_context: str = ""        # what the user was told / typed around this payment
    remote_access_app_open: bool = False
    recent_txn_count_5min: int = 0   # how many transfers in the last 5 minutes


@dataclass
class RiskSignal:
    code: str
    weight: int
    explanation: str


@dataclass
class RiskResult:
    score: int
    level: RiskLevel
    action: Action
    signals: list[RiskSignal] = field(default_factory=list)

    @property
    def triggered(self) -> bool:
        return bool(self.signals)

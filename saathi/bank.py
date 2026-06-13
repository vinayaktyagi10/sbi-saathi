"""Mock banking core — in-memory stand-in for SBI / YONO / UPI APIs.

Lets the whole MVP run offline. In production each method becomes a real call
into SBI's core banking + UPI rails; the agent and fraud engine above don't
change.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from .models import Payee, Transaction, User


class MockBank:
    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._seed()

    def _seed(self) -> None:
        # A realistic Saathi target: a semi-urban, first-time digital user.
        self._users["U1001"] = User(
            user_id="U1001",
            name="Lakshmi",
            language="hi",
            balance=48250.0,
            is_first_time_digital=True,
            avg_txn_amount=1200.0,
            max_txn_amount=5000.0,
            known_payees=["Suresh Kirana", "Electricity Board"],
        )

    def get_user(self, user_id: str) -> User:
        return self._users[user_id]

    def balance(self, user_id: str) -> float:
        return self._users[user_id].balance

    def make_payee(self, name: str, upi_id: str, minutes_ago: float = 0.0,
                   in_contacts: bool = False) -> Payee:
        return Payee(name=name, upi_id=upi_id,
                     added_at=datetime.now() - timedelta(minutes=minutes_ago),
                     in_contacts=in_contacts)

    def execute(self, txn: Transaction) -> bool:
        """Move the money. Returns True on success."""
        user = self._users[txn.user_id]
        if txn.amount > user.balance:
            return False
        user.balance -= txn.amount
        if txn.payee.name not in user.known_payees:
            user.known_payees.append(txn.payee.name)
        return True

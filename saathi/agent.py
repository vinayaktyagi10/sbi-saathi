"""The agent — Saathi's orchestrator.

This is what makes Saathi *agentic* rather than a chatbot: it forms a plan,
calls tools (bank APIs), and gates money movement through the fraud engine,
taking the protective action itself instead of just answering questions.

Pending-payment state lets the agent pause a risky transfer, explain it in the
user's language, and only complete it on explicit re-confirmation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .bank import MockBank
from .brain import Brain, Intent, RuleBasedBrain
from .fraud_engine import FraudEngine
from .language import say
from .models import Action, RiskResult, Transaction, User


@dataclass
class SessionContext:
    """Signals a real client would capture from the device / conversation."""
    remote_access_app_open: bool = False
    recent_txn_count_5min: int = 0
    last_message: str = ""           # surrounding conversation for scam detection


@dataclass
class AgentReply:
    text: str
    risk: Optional[RiskResult] = None
    awaiting_confirmation: bool = False
    blocked: bool = False


class SaathiAgent:
    def __init__(self, bank: MockBank, brain: Brain | None = None) -> None:
        self.bank = bank
        self.brain = brain or RuleBasedBrain()
        self.fraud = FraudEngine()
        self._pending: dict[str, Transaction] = {}   # user_id -> held txn

    def handle(self, user_id: str, text: str,
               ctx: SessionContext | None = None) -> AgentReply:
        ctx = ctx or SessionContext()
        user = self.bank.get_user(user_id)

        # If a payment is held awaiting the user's decision, interpret this turn
        # as their answer rather than a fresh intent.
        if user_id in self._pending:
            return self._resolve_pending(user, text)

        intent = self.brain.understand(text)
        return self._route(user, intent, ctx)

    # --- intent routing ----------------------------------------------------
    def _route(self, user: User, intent: Intent,
               ctx: SessionContext) -> AgentReply:
        if intent.name == "greet":
            return AgentReply(say(user.language, "greet", name=user.name))
        if intent.name == "balance":
            return AgentReply(say(user.language, "balance", balance=user.balance))
        if intent.name == "invest":
            return AgentReply(say(user.language, "invest"))
        if intent.name == "help":
            return AgentReply(say(user.language, "help"))
        if intent.name == "pay":
            return self._handle_pay(user, intent, ctx)
        return AgentReply(say(user.language, "unknown"))

    # --- the protected payment flow ---------------------------------------
    def _handle_pay(self, user: User, intent: Intent,
                    ctx: SessionContext) -> AgentReply:
        if not intent.amount or not intent.payee:
            return AgentReply(say(user.language, "ask_amount"))

        if intent.amount > user.balance:
            return AgentReply(say(user.language, "low_balance",
                                  balance=user.balance))

        # Build the transaction with all the context the fraud engine needs.
        payee = self.bank.make_payee(intent.payee, upi_id="unknown@upi",
                                     minutes_ago=2.0)
        txn = Transaction(
            user_id=user.user_id, amount=intent.amount, payee=payee,
            message_context=ctx.last_message,
            remote_access_app_open=ctx.remote_access_app_open,
            recent_txn_count_5min=ctx.recent_txn_count_5min,
        )

        risk = self.fraud.assess(user, txn)

        if risk.action == Action.ALLOW:
            return self._complete(user, txn, risk)

        if risk.action == Action.SOFT_WARN:
            reply = self._complete(user, txn, risk)
            reply.text = self._warn_banner(risk) + "\n" + reply.text
            return reply

        # HARD_CONFIRM or BLOCK → hold the payment and explain.
        self._pending[user.user_id] = txn
        return AgentReply(
            text=self._intervention_text(user, txn, risk),
            risk=risk,
            awaiting_confirmation=(risk.action == Action.HARD_CONFIRM),
            blocked=(risk.action == Action.BLOCK),
        )

    def _resolve_pending(self, user: User, text: str) -> AgentReply:
        txn = self._pending.pop(user.user_id)
        if any(w in text.lower() for w in
               ["yes", "confirm", "haan", "ok", "proceed", "sure"]):
            risk = self.fraud.assess(user, txn)
            return self._complete(user, txn, risk, forced=True)
        return AgentReply("Okay, I've cancelled that payment. Your money is safe.")

    def _complete(self, user: User, txn: Transaction, risk: RiskResult,
                  forced: bool = False) -> AgentReply:
        self.bank.execute(txn)
        return AgentReply(
            text=say(user.language, "paid", amount=txn.amount,
                     payee=txn.payee.name, balance=user.balance),
            risk=risk if risk.triggered else None,
        )

    # --- presentation helpers ---------------------------------------------
    def _warn_banner(self, risk: RiskResult) -> str:
        top = risk.signals[0].explanation
        return f"⚠️ Heads up ({risk.level.value}): {top}"

    def _intervention_text(self, user: User, txn: Transaction,
                           risk: RiskResult) -> str:
        bullets = "\n".join(f"  • {s.explanation}" for s in risk.signals)
        head = ("🛑 I've STOPPED this payment to protect you."
                if risk.action == Action.BLOCK
                else "✋ Wait — let me check this with you before sending.")
        tail = ("This payment is blocked for now. If you're sure, we'll verify it "
                "together safely — never under pressure from a caller."
                if risk.action == Action.BLOCK
                else f"If you still want to pay ₹{txn.amount:,.0f} to "
                     f"{txn.payee.name}, reply 'yes'. Reply 'no' to cancel.")
        return f"{head}\n\nWhy I'm cautious:\n{bullets}\n\n{tail}"

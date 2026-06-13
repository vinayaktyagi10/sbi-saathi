"""Real-time fraud risk engine — the differentiator of SBI Saathi.

This is deliberately rule-based and transparent rather than a black-box model.
For a hackathon MVP that matters: every decision is explainable to a banking
judge, and each rule maps to a documented Indian fraud typology (digital-arrest
scams, remote-access takeovers, mule-account layering, phishing urgency).

In production these weighted rules become features feeding an ML model trained
on SBI's transaction graph (see ROADMAP in README). The interface stays the same.
"""
from __future__ import annotations

from datetime import datetime

from .models import Action, RiskLevel, RiskResult, RiskSignal, Transaction, User

# --- Lexicons for pressure / scam-script detection -------------------------
# Cues lifted from real Indian scam patterns: digital arrest, fake KYC, fake
# refund, "account blocked", impersonation of police / RBI / bank officials.
URGENCY_CUES = [
    "urgent", "immediately", "right now", "last chance", "within 10 minutes",
    "account blocked", "account will be blocked", "kyc expired", "kyc update",
    "verify now", "otp", "share otp", "refund", "lottery", "reward", "prize",
]
AUTHORITY_CUES = [
    "police", "cbi", "arrest", "digital arrest", "rbi", "income tax",
    "customs", "court", "legal action", "fir", "officer", "fedex",
]


def _contains_any(text: str, cues: list[str]) -> list[str]:
    low = text.lower()
    return [c for c in cues if c in low]


class FraudEngine:
    """Scores a transaction 0-100 and recommends an action."""

    # Score thresholds → risk level
    THRESHOLDS = [(75, RiskLevel.CRITICAL), (45, RiskLevel.HIGH),
                  (20, RiskLevel.MEDIUM), (0, RiskLevel.LOW)]

    # Risk level → default action
    ACTIONS = {
        RiskLevel.CRITICAL: Action.BLOCK,
        RiskLevel.HIGH: Action.HARD_CONFIRM,
        RiskLevel.MEDIUM: Action.SOFT_WARN,
        RiskLevel.LOW: Action.ALLOW,
    }

    def assess(self, user: User, txn: Transaction) -> RiskResult:
        signals: list[RiskSignal] = []

        # 1. Remote-access / screen-sharing app open during a payment.
        #    Near-certain takeover scam (AnyDesk/TeamViewer social engineering).
        if txn.remote_access_app_open:
            signals.append(RiskSignal(
                "REMOTE_ACCESS", 60,
                "A screen-sharing app is open. Real bank staff never ask you to "
                "share your screen while you pay."))

        # 2. Authority impersonation + urgency in the surrounding conversation.
        authority = _contains_any(txn.message_context, AUTHORITY_CUES)
        urgency = _contains_any(txn.message_context, URGENCY_CUES)
        if authority and urgency:
            signals.append(RiskSignal(
                "DIGITAL_ARREST", 55,
                "This looks like a 'digital arrest' / impersonation scam: someone "
                "claiming authority is pressuring you to pay urgently."))
        elif authority:
            signals.append(RiskSignal(
                "AUTHORITY_PRESSURE", 25,
                "Someone is invoking police/RBI/court. Genuine agencies never "
                "collect money over a payment app."))
        elif urgency:
            signals.append(RiskSignal(
                "URGENCY_PRESSURE", 20,
                "There is urgency/OTP/reward pressure around this payment — a "
                "common scam tactic."))

        # 3. Brand-new payee (added very recently) being paid for the first time.
        age_minutes = (datetime.now() - txn.payee.added_at).total_seconds() / 60
        first_time_payee = txn.payee.name not in user.known_payees
        if first_time_payee and age_minutes <= 30:
            signals.append(RiskSignal(
                "NEW_PAYEE", 25,
                f"You are paying {txn.payee.name} for the first time, added just "
                f"{int(age_minutes)} min ago."))
        elif first_time_payee:
            signals.append(RiskSignal(
                "UNKNOWN_PAYEE", 10,
                f"{txn.payee.name} is not in your usual payees."))

        # 4. Amount anomaly vs the user's own history.
        ceiling = max(user.max_txn_amount, user.avg_txn_amount * 3, 1)
        if txn.amount > ceiling:
            signals.append(RiskSignal(
                "AMOUNT_ANOMALY", 20,
                f"₹{txn.amount:,.0f} is much higher than your usual payments."))

        # 5. Rapid layering — multiple transfers in minutes (mule pattern).
        if txn.recent_txn_count_5min >= 3:
            signals.append(RiskSignal(
                "RAPID_LAYERING", 20,
                "Several quick transfers in a row — a pattern seen in money-mule "
                "fraud."))

        # 6. Extra care for the people Saathi exists to protect.
        if user.is_first_time_digital and signals:
            signals.append(RiskSignal(
                "VULNERABLE_USER", 10,
                "First-time digital user — applying extra caution."))

        score = min(100, sum(s.weight for s in signals))
        level = next(lvl for thresh, lvl in self.THRESHOLDS if score >= thresh)
        return RiskResult(score=score, level=level,
                          action=self.ACTIONS[level], signals=signals)

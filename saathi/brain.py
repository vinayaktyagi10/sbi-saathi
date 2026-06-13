"""The 'brain' — intent understanding for the agent.

MVP ships an offline, deterministic parser so the repo runs with no API keys.
Swapping in a real LLM (Anthropic, or an Indic model like Sarvam for vernacular
voice) is a one-class change: implement `Brain.understand` and plug it into the
Agent. The rest of the system is unchanged.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class Intent:
    name: str                       # greet | balance | pay | invest | help | unknown
    amount: Optional[float] = None
    payee: Optional[str] = None


class Brain(Protocol):
    def understand(self, text: str) -> Intent: ...


class RuleBasedBrain:
    """Lightweight intent parser. Good enough to demo the agent end-to-end."""

    _AMOUNT = re.compile(r"(?:rs\.?|₹|inr)?\s*([\d,]+(?:\.\d+)?)", re.I)
    _TO = re.compile(r"\bto\s+([A-Za-z][\w' ]+?)(?:\s+rs|\s+₹|\s+\d|$)", re.I)

    def understand(self, text: str) -> Intent:
        t = text.lower().strip()

        if t in {"hi", "hello", "namaste", "hey", "start", "hi saathi"}:
            return Intent("greet")
        if any(w in t for w in ["balance", "how much", "kitna", "paisa hai"]):
            return Intent("balance")
        if any(w in t for w in ["invest", "sip", "fd", "deposit", "mutual",
                                 "save", "saving", "bachat"]):
            return Intent("invest")
        if any(w in t for w in ["help", "scam", "fraud", "safe", "madad"]):
            return Intent("help")
        if any(w in t for w in ["pay", "send", "transfer", "bhej"]):
            amount = None
            m = self._AMOUNT.search(t)
            if m:
                amount = float(m.group(1).replace(",", ""))
            payee = None
            mt = self._TO.search(text)
            if mt:
                payee = mt.group(1).strip().title()
            return Intent("pay", amount=amount, payee=payee)

        return Intent("unknown")


# --- Hook for a real LLM (left unimplemented on purpose) -------------------
class LLMBrain:
    """Drop-in replacement. Wire up your provider here.

    Example (Anthropic):
        import anthropic
        client = anthropic.Anthropic()
        ... call messages.create with a tool/function schema that returns
            {name, amount, payee} and map it to Intent ...
    """

    def __init__(self, client=None):
        self.client = client

    def understand(self, text: str) -> Intent:  # pragma: no cover
        raise NotImplementedError(
            "Plug your LLM here. RuleBasedBrain runs the MVP offline.")

"""Vernacular response layer.

A tiny phrasebook to *demonstrate* the voice-first, own-language principle that
makes Saathi work for first-time users. Two languages are enough to prove the
architecture; production routes generation through an Indic LLM + TTS so every
reply (including fraud warnings) is spoken in the user's language.
"""
from __future__ import annotations

PHRASES: dict[str, dict[str, str]] = {
    "en": {
        "greet": "Namaste {name}! I'm Saathi. I can check your balance, pay "
                 "someone, or start a small savings — what would you like?",
        "balance": "Your balance is ₹{balance:,.0f}.",
        "ask_amount": "Sure. How much, and to whom?",
        "paid": "Done. ₹{amount:,.0f} sent to {payee}. New balance ₹{balance:,.0f}.",
        "low_balance": "That's more than your balance of ₹{balance:,.0f}.",
        "invest": "Good thinking. You can start a SIP with as little as ₹500/month. "
                  "Shall I set one up step by step?",
        "help": "You're safe with me. I watch every payment and stop anything "
                "that looks like a scam before your money leaves.",
        "unknown": "I didn't catch that. You can say things like 'check balance' "
                   "or 'pay 500 to Suresh'.",
    },
    "hi": {
        "greet": "Namaste {name}! Main Saathi hoon. Balance dekhna, kisi ko paise "
                 "bhejna, ya chhoti bachat shuru karni ho — bataiye?",
        "balance": "Aapka balance ₹{balance:,.0f} hai.",
        "ask_amount": "Theek hai. Kitne paise, aur kisko?",
        "paid": "Ho gaya. ₹{amount:,.0f} {payee} ko bhej diye. Naya balance "
                "₹{balance:,.0f}.",
        "low_balance": "Yeh aapke balance ₹{balance:,.0f} se zyada hai.",
        "invest": "Achhi soch. Aap sirf ₹500/mahina se SIP shuru kar sakte hain. "
                  "Main step-by-step laga doon?",
        "help": "Aap mere saath surakshit hain. Main har payment par nazar rakhta "
                "hoon aur dhokhe wali transaction rok deta hoon.",
        "unknown": "Samajh nahi aaya. Aap keh sakte hain 'balance batao' ya "
                   "'Suresh ko 500 bhejo'.",
    },
}


def say(language: str, key: str, **kw) -> str:
    lang = PHRASES.get(language, PHRASES["en"])
    template = lang.get(key, PHRASES["en"][key])
    return template.format(**kw)

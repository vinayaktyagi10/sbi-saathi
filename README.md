# SBI Saathi 🛡️

**A vernacular, voice-first agentic companion that drives digital adoption by building trust.**

> SBI Hackathon @ GFF 2026 · Theme: *Agentic AI & Emerging Tech* · Problem Statement: *Digital Adoption*

---

## The insight

SBI holds **500M+ accounts but only ~75M active YONO users.** The 425M who stay
away are largely **rural, elderly, first-time digital users** — the *same* people
losing **₹22,000+ crore a year** to digital fraud.

People don't go digital because they're scared of being scammed. **Fear is the
adoption barrier. So safety is the growth lever.**

Saathi is an agentic companion that wins adoption by *protecting* the user: it
onboards them in their own language, nudges them gently toward digital services,
and **stops scams in real time before the money leaves.**

## Why it's *agentic*, not a chatbot

It doesn't just answer — it **acts**. It plans, calls banking tools, and gates
every payment through a fraud engine, **pausing or blocking** a transfer itself
and re-confirming with the user instead of letting them walk into a scam.

```
 User (voice / text, any language)
        │
        ▼
 ┌──────────────┐   intent     ┌──────────────┐
 │   Brain      │─────────────▶│   Agent      │  plans + acts
 │ (LLM / rules)│              │ orchestrator │
 └──────────────┘              └──────┬───────┘
                                      │ every money movement
                                      ▼
                              ┌────────────────┐
                              │  Fraud Engine  │  ◀── the differentiator
                              │ score + action │
                              └──────┬─────────┘
                       ALLOW / WARN / PAUSE / BLOCK
                                      │
                                      ▼
                              ┌────────────────┐
                              │  Bank / UPI    │  (mocked in MVP)
                              └────────────────┘
```

## Quickstart

**Zero dependencies — runs on the Python standard library. No API keys.**

```bash
# 1. Scripted story for judges / your demo video
python run_demo.py

# 2. Interactive browser demo
python app.py        # then open http://localhost:8000

# 3. Tests
python -m unittest discover -s tests -v
```

In the browser demo, flip the **Scam-call pressure** / **Screen-share app open**
toggles, then try `Send 45000 to Verification Officer` and watch Saathi shift
into its protective guard state.

## What the fraud engine catches (MVP)

Each rule maps to a documented Indian fraud typology — and every decision is
**explainable** (no black box), which matters to a banking judge:

| Signal | Real-world pattern |
|---|---|
| `REMOTE_ACCESS` | AnyDesk/TeamViewer screen-share takeover |
| `DIGITAL_ARREST` | Fake police/RBI/court urgency to extort a payment |
| `NEW_PAYEE` | First payment to a payee added minutes ago |
| `AMOUNT_ANOMALY` | Far above the user's own history |
| `RAPID_LAYERING` | Many quick transfers — money-mule behaviour |
| `VULNERABLE_USER` | Extra caution for first-time digital users |

## Project structure

```
saathi/
  agent.py          # orchestrator: plans, acts, gates payments
  fraud_engine.py   # the differentiator: transparent risk scoring
  brain.py          # intent understanding (rule-based now, LLM-ready)
  bank.py           # mock SBI/UPI core (in-memory)
  language.py       # vernacular response layer (en + hi shown)
  models.py         # data structures
app.py              # stdlib web server + JSON API
run_demo.py         # scripted CLI walkthrough
web/index.html      # chat UI with the signature guard state
tests/              # fraud-engine unit tests
```

## From MVP → prototype phase

This repo is the **idea-round starting point**. Path to the prototype round:

- **Brain:** swap `RuleBasedBrain` for `LLMBrain` — an Indic LLM (e.g. Sarvam)
  + speech-to-text/TTS for true voice-first vernacular onboarding. Interface is
  already defined in `brain.py`.
- **Fraud engine:** today's weighted rules become **features for an ML model**
  trained on SBI's transaction graph, aligned with RBI / MuleHunter typologies.
  The `assess()` contract stays identical.
- **Bank:** replace `MockBank` with real YONO / UPI sandbox APIs.
- **Proactive nudges:** event-driven engine reacting to FD maturity, salary
  credit, recurring bills, life events.

## Note

Built as a hackathon MVP to demonstrate the core thesis end-to-end. Figures cited
are from public reporting on SBI/YONO and RBI fraud data (see the idea deck).

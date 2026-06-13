"""Scripted demo of SBI Saathi. Run:  python run_demo.py

Walks through the scenarios that tell the story for judges:
  1. A normal, safe payment — Saathi stays out of the way.
  2. A 'digital arrest' scam — Saathi blocks it and explains in plain language.
  3. A remote-access (screen-share) takeover — Saathi blocks it.
  4. Adoption moments — balance check + a gentle SIP nudge.
No API keys, no internet. Pure logic.
"""
from saathi import MockBank, SaathiAgent, SessionContext

LINE = "─" * 64


def turn(agent, uid, text, ctx=None, who="Lakshmi"):
    print(f"\n👤 {who}: {text}")
    reply = agent.handle(uid, text, ctx)
    lines = reply.text.splitlines()
    for i, line in enumerate(lines):
        prefix = "🤖 Saathi: " if i == 0 else "          "
        print(prefix + line)
    return reply


def scenario(title):
    print(f"\n{LINE}\n {title}\n{LINE}")


def main():
    bank = MockBank()
    agent = SaathiAgent(bank)
    uid = "U1001"

    print("SBI Saathi — MVP demo")
    print("User: Lakshmi, first-time digital user, balance ₹48,250\n")

    scenario("1. A normal, safe payment — Saathi stays out of the way")
    turn(agent, uid, "Hi")
    turn(agent, uid, "Pay 800 to Suresh Kirana")

    scenario("2. 'Digital arrest' scam — caller pressures an urgent payment")
    ctx = SessionContext(
        last_message="Police officer says my account is blocked, I must pay "
                     "urgently or face arrest",
        recent_txn_count_5min=0)
    turn(agent, uid, "Send 45000 to Verification Officer", ctx)
    turn(agent, uid, "no")   # user trusts Saathi and backs out

    scenario("3. Remote-access takeover — a screen-share app is open")
    ctx = SessionContext(remote_access_app_open=True,
                         last_message="support agent told me to install AnyDesk")
    turn(agent, uid, "Transfer 20000 to Refund Support", ctx)
    turn(agent, uid, "no")

    scenario("4. Adoption moments — balance + a gentle savings nudge")
    turn(agent, uid, "balance kitna hai")
    turn(agent, uid, "I want to start saving")

    print(f"\n{LINE}\n Net: scams stopped, safe payments untouched, and a")
    print(" hesitant user nudged one step further into digital banking.")
    print(LINE)


if __name__ == "__main__":
    main()

"""Tests for the fraud engine. Run:  python -m pytest -q  (or: python -m unittest)"""
import unittest

from saathi.bank import MockBank
from saathi.fraud_engine import FraudEngine
from saathi.models import Action, RiskLevel, Transaction


class FraudEngineTests(unittest.TestCase):
    def setUp(self):
        self.bank = MockBank()
        self.user = self.bank.get_user("U1001")
        self.engine = FraudEngine()

    def _txn(self, amount, payee_name="Suresh Kirana", minutes_ago=120.0,
             **kw):
        payee = self.bank.make_payee(payee_name, "x@upi", minutes_ago=minutes_ago)
        return Transaction(user_id="U1001", amount=amount, payee=payee, **kw)

    def test_normal_payment_is_allowed(self):
        r = self.engine.assess(self.user, self._txn(800))
        self.assertEqual(r.action, Action.ALLOW)
        self.assertEqual(r.level, RiskLevel.LOW)

    def test_digital_arrest_scam_is_blocked(self):
        txn = self._txn(45000, payee_name="Verification Officer", minutes_ago=2,
                        message_context="police say account blocked, pay urgently")
        r = self.engine.assess(self.user, txn)
        self.assertEqual(r.action, Action.BLOCK)
        self.assertTrue(any(s.code == "DIGITAL_ARREST" for s in r.signals))

    def test_remote_access_is_blocked(self):
        txn = self._txn(20000, payee_name="Refund Support", minutes_ago=1,
                        remote_access_app_open=True)
        r = self.engine.assess(self.user, txn)
        self.assertEqual(r.action, Action.BLOCK)
        self.assertTrue(any(s.code == "REMOTE_ACCESS" for s in r.signals))

    def test_mule_layering_pattern_raises_risk(self):
        txn = self._txn(3000, payee_name="New Guy", minutes_ago=1,
                        recent_txn_count_5min=4)
        r = self.engine.assess(self.user, txn)
        self.assertTrue(any(s.code == "RAPID_LAYERING" for s in r.signals))
        self.assertNotEqual(r.action, Action.ALLOW)

    def test_known_payee_normal_amount_stays_low(self):
        r = self.engine.assess(self.user, self._txn(1500))
        self.assertEqual(r.level, RiskLevel.LOW)


if __name__ == "__main__":
    unittest.main()

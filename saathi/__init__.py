"""SBI Saathi — a vernacular, agentic banking companion that drives digital
adoption by building trust (real-time fraud guardian)."""

from .agent import SaathiAgent, SessionContext, AgentReply
from .bank import MockBank
from .fraud_engine import FraudEngine
from .models import RiskLevel, Action

__all__ = [
    "SaathiAgent", "SessionContext", "AgentReply",
    "MockBank", "FraudEngine", "RiskLevel", "Action",
]
__version__ = "0.1.0"

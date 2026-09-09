"""Blind scientific decision-recovery Agent for PUR-Essay (PUR-RECOVER V1).

The Agent never defines scientific truth. `pur_science` freezes the answer; this package
hides it, exposes deterministic tools, runs LLM baselines and scores recovery.
"""

from .agent import run_once
from .conditions import CONDITIONS, Condition, get_condition
from .data_access import BlindBundle, BundleReader
from .evaluator import evaluate_decision, evaluate_run_record, remap_decision
from .llm_client import MockLLMClient, OpenAICompatibleClient, OpenAIResponsesClient, make_client
from .metrics import score_decision
from .schemas import AgentDecision, parse_decision
from .strategy import RecoveryStrategy, StrategyStage
from .tools import DecisionToolbox

__all__ = [
    "run_once", "CONDITIONS", "Condition", "get_condition", "BlindBundle", "BundleReader",
    "evaluate_decision", "evaluate_run_record", "remap_decision", "MockLLMClient", "OpenAICompatibleClient",
    "OpenAIResponsesClient", "make_client", "score_decision", "AgentDecision", "parse_decision",
    "RecoveryStrategy", "StrategyStage", "DecisionToolbox",
]

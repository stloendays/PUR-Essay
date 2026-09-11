"""Blind scientific decision-recovery Agent for PUR-Essay (PUR-RECOVER V1 and V2).

The Agent never defines scientific truth. `pur_science` freezes the answer; this package
hides it, exposes deterministic tools, runs LLM baselines and scores recovery.

V2 is an orchestration version, not a science version: same frozen frontier, same gold, same
primary metric, with claim-level evidence planning, counterfactual challenge, dual-path
verification, a canonical constraint ontology and a machine-computed decision certificate.
"""

from .agent import run_once
from .certificate import build_certificate, ontology_check, procedural_gate
from .challenge_tools import ChallengeToolbox
from .conditions import CONDITIONS, Condition, get_condition
from .crosspath import verify_backward_threshold
from .data_access import BlindBundle, BundleReader
from .evaluator import evaluate_decision, evaluate_run_record, remap_decision
from .evidence import CLAIM_EVIDENCE_PATHS, EvidencePlanner
from .llm_client import MockLLMClient, OpenAICompatibleClient, OpenAIResponsesClient, make_client
from .metrics import score_decision, score_decision_v2
from .ontology import canonical_constraint, normalize_quantity, same_constraint
from .schemas import AgentDecision, AgentDecisionV2, parse_decision, parse_decision_v2
from .strategy import RecoveryStrategy, StrategyStage, StrategyStageV2, V2Policy
from .tools import DecisionToolbox
from .tools_v2 import V2Toolbox

__all__ = [
    "run_once", "CONDITIONS", "Condition", "get_condition", "BlindBundle", "BundleReader",
    "evaluate_decision", "evaluate_run_record", "remap_decision", "MockLLMClient", "OpenAICompatibleClient",
    "OpenAIResponsesClient", "make_client", "score_decision", "AgentDecision", "parse_decision",
    "RecoveryStrategy", "StrategyStage", "DecisionToolbox",
    # PUR-RECOVER V2
    "build_certificate", "ontology_check", "procedural_gate", "ChallengeToolbox", "verify_backward_threshold",
    "CLAIM_EVIDENCE_PATHS", "EvidencePlanner", "score_decision_v2", "canonical_constraint", "normalize_quantity",
    "same_constraint", "AgentDecisionV2", "parse_decision_v2", "StrategyStageV2", "V2Policy", "V2Toolbox",
]

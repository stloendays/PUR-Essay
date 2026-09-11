"""Claim-evidence dependency graph (PUR-RECOVER V2, Stage A).

V1 gated finalisation on a fixed checklist: every required tool family had to appear in the
trace. That conflates "did the Agent prove its claims" with "did the Agent press every
button". V2 replaces it with a claim-level contract: each final scientific claim declares
the *minimum sufficient* deterministic evidence that supports it, and more than one
admissible derivation may exist.

The pilot demonstrated why this matters. With `solve_backward_threshold` removed, the model
still recovered the continuous NCO:OH threshold to 1e-8 by combining `local_nco_sweep` with
`calculate_mdi_fraction`. That is a genuine second derivation of the same frozen quantity,
not luck, so V2 registers it as an admissible evidence path.

Nothing here evaluates whether a claim is *correct* — that is evaluator-side. This module
only asks whether the claim is *supported*.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

EVIDENCE_GRAPH_VERSION = "PUR_EVIDENCE_V2"

# claim -> ordered admissible evidence paths; each path is a set of tools that must all have
# been called. The first path is the direct derivation, later paths are reconstructions.
CLAIM_EVIDENCE_PATHS: dict[str, tuple[tuple[str, ...], ...]] = {
    "property_winner": (
        ("rank_property",),
    ),
    "constrained_winner": (
        ("rank_constrained",),
        # scan the property ranking downward, auditing each candidate until one is feasible
        ("rank_property", "constraint_audit"),
    ),
    "robust_winner": (
        ("rank_robust",),
    ),
    "active_constraint": (
        ("constraint_audit",),
        # inspect_candidate returns the per-check booleans; dataset_summary carries the bounds
        ("inspect_candidate", "dataset_summary"),
    ),
    "backward_threshold": (
        ("solve_backward_threshold",),
        # Path B: reconstruct the MDI-demand manifold from the blend's own grid
        ("local_nco_sweep", "calculate_mdi_fraction"),
    ),
    "reachable_grid": (
        ("check_reachability",),
        # the sweep returns every grid point of the blend with its MDI fraction
        ("local_nco_sweep",),
    ),
    "reachability": (
        ("check_reachability",),
        ("local_nco_sweep",),
    ),
    "nco_direction": (
        ("local_nco_sweep",),
    ),
    "composition_direction": (
        ("local_composition_sweep",),
    ),
}

REQUIRED_CLAIMS = tuple(CLAIM_EVIDENCE_PATHS)

# Claims whose critical quantity has two independent derivations that V2 cross-checks.
DUAL_PATH_CLAIMS = ("backward_threshold",)


@dataclass(frozen=True)
class ClaimStatus:
    claim: str
    satisfied: bool
    admissible: bool
    satisfied_path: tuple[str, ...] | None
    admissible_paths: tuple[tuple[str, ...], ...]
    missing_tools: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim": self.claim,
            "satisfied": self.satisfied,
            "admissible": self.admissible,
            "satisfied_path": list(self.satisfied_path) if self.satisfied_path else None,
            "admissible_paths": [list(p) for p in self.admissible_paths],
            "missing_tools": list(self.missing_tools),
        }


@dataclass(frozen=True)
class EvidenceCoverage:
    claims: tuple[ClaimStatus, ...]
    satisfied: int
    required: int
    unsatisfiable: tuple[str, ...]
    called_tools: tuple[str, ...] = ()

    @property
    def complete(self) -> bool:
        return self.satisfied >= self.required

    @property
    def missing_claims(self) -> tuple[str, ...]:
        return tuple(c.claim for c in self.claims if c.admissible and not c.satisfied)

    def missing_tools(self) -> tuple[str, ...]:
        """Cheapest tools that would close the open claims: one shortest path per claim."""
        out: list[str] = []
        for c in self.claims:
            if c.admissible and not c.satisfied and c.missing_tools:
                for t in c.missing_tools:
                    if t not in out:
                        out.append(t)
        return tuple(out)

    def used_evidence_tools(self) -> tuple[str, ...]:
        """Tools on the minimum-sufficient path actually taken for each satisfied claim."""
        out: list[str] = []
        for c in self.claims:
            for t in (c.satisfied_path or ()):
                if t not in out:
                    out.append(t)
        return tuple(out)

    def purposeful_tools(self) -> tuple[str, ...]:
        """Every tool on *any* admissible path of a satisfied claim, plus the opening audit.

        Wider than `used_evidence_tools` on purpose. A V2 run is required to compute the
        second admissible derivation of the backward threshold, so the Path B tools are
        purposeful even when Path A is the one that carried the claim. Calls outside this set
        are genuinely off-plan.
        """
        out: list[str] = ["dataset_summary"]
        for c in self.claims:
            if not c.satisfied:
                continue
            for path in c.admissible_paths:
                for t in path:
                    if t not in out:
                        out.append(t)
        return tuple(out)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": EVIDENCE_GRAPH_VERSION,
            "satisfied": self.satisfied,
            "required": self.required,
            "complete": self.complete,
            "unsatisfiable_claims": list(self.unsatisfiable),
            "missing_claims": list(self.missing_claims),
            "claims": [c.to_dict() for c in self.claims],
        }


class EvidencePlanner:
    """Builds the claim-evidence plan and scores a trace against it."""

    def __init__(self, paths: dict[str, tuple[tuple[str, ...], ...]] | None = None) -> None:
        self.paths = dict(paths or CLAIM_EVIDENCE_PATHS)

    def admissible_paths(self, claim: str, available_tools: Iterable[str] | None) -> tuple[tuple[str, ...], ...]:
        """Paths whose tools all exist in this condition. Ablations legitimately remove paths."""
        paths = self.paths.get(claim, ())
        if available_tools is None:
            return paths
        available = set(available_tools)
        return tuple(p for p in paths if set(p).issubset(available))

    def plan(self, available_tools: Iterable[str] | None = None) -> dict[str, Any]:
        """Machine-readable plan logged with every V2 run."""
        available = None if available_tools is None else sorted(set(available_tools))
        claims = []
        for claim in REQUIRED_CLAIMS:
            adm = self.admissible_paths(claim, available)
            claims.append({
                "claim": claim,
                "admissible_evidence_paths": [list(p) for p in adm],
                "minimum_sufficient_tools": list(min(adm, key=len)) if adm else [],
                "admissible": bool(adm),
                "dual_path_checked": claim in DUAL_PATH_CLAIMS and len(adm) >= 2,
            })
        return {
            "version": EVIDENCE_GRAPH_VERSION,
            "available_tools": available,
            "required_claims": list(REQUIRED_CLAIMS),
            "n_admissible_claims": sum(1 for c in claims if c["admissible"]),
            "claims": claims,
        }

    def coverage(self, called_tools: Iterable[str], available_tools: Iterable[str] | None = None) -> EvidenceCoverage:
        called = list(called_tools)
        called_set = set(called)
        statuses: list[ClaimStatus] = []
        unsatisfiable: list[str] = []
        for claim in REQUIRED_CLAIMS:
            adm = self.admissible_paths(claim, available_tools)
            if not adm:
                unsatisfiable.append(claim)
                statuses.append(ClaimStatus(claim, False, False, None, (), ()))
                continue
            hit = next((p for p in adm if set(p).issubset(called_set)), None)
            missing: tuple[str, ...] = ()
            if hit is None:
                best = min(adm, key=lambda p: len(set(p) - called_set))
                missing = tuple(t for t in best if t not in called_set)
            statuses.append(ClaimStatus(claim, hit is not None, True, hit, adm, missing))
        required = sum(1 for s in statuses if s.admissible)
        satisfied = sum(1 for s in statuses if s.satisfied)
        return EvidenceCoverage(tuple(statuses), satisfied, required, tuple(unsatisfiable), tuple(called))


def unnecessary_tool_calls(trace: Iterable[Any], coverage: EvidenceCoverage) -> dict[str, Any]:
    """Calls not attributable to a satisfied minimum-sufficient evidence path.

    Accepts either the full trace (entries with `tool` and `arguments`) or a plain list of
    tool names. A repeat of the same tool with *different* arguments is not redundant:
    `local_nco_sweep` must legitimately be run on the property winner's blend for the
    backward reconstruction and on the decision point for the local trend. Only an identical
    (tool, arguments) pair repeated after the claim is already satisfied counts as redundant.

    The caller separately excludes the required challenge tools, so a V2 run is not penalised
    for performing the challenge stage its contract demands.
    """
    entries: list[tuple[str, str]] = []
    for item in trace:
        if isinstance(item, dict):
            entries.append((str(item.get("tool")), json.dumps(item.get("arguments") or {}, sort_keys=True)))
        else:
            entries.append((str(item), ""))
    useful = set(coverage.used_evidence_tools())
    seen_names: set[str] = set()
    seen_calls: set[tuple[str, str]] = set()
    unnecessary = 0
    redundant_repeats = 0
    for name, args in entries:
        if name in useful and (name, args) not in seen_calls:
            seen_names.add(name)
            seen_calls.add((name, args))
            continue
        if (name, args) in seen_calls:
            redundant_repeats += 1
        unnecessary += 1
    return {
        "total_calls": len(entries),
        "evidence_bearing_calls": len(seen_names),
        "distinct_evidence_calls": len(seen_calls),
        "unnecessary_calls": unnecessary,
        "redundant_repeat_calls": redundant_repeats,
    }

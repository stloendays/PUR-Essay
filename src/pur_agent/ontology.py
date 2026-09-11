"""Canonical scientific ontology for constraint identity (PUR-RECOVER V2).

The first real-API pilot produced a run whose science was correct but whose strict audit
field failed only because the model wrote ``mdi_fraction_min`` where the frozen gold writes
``mdi_fraction``. That is an interface defect, not a scientific one, and V2 fixes it at the
source: every V2 tool output, prompt and log expresses a constraint as one canonical object

    {"quantity": "mdi_fraction", "operator": ">=", "threshold": 0.35}

`quantity` is the measured scientific quantity, `operator` the direction of the binding
bound and `threshold` its value. Aliases are recognised on input so a model that still
writes a legacy spelling is scored as scientifically correct and schema-incorrect, which
are deliberately separate metrics.

This module changes no science. It never renames a `pur_science` field, never rewrites a
frozen gold file, and is not applied retroactively to V1 records.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

CANONICAL_VERSION = "PUR_ONTOLOGY_V2"

OPERATORS = (">=", "<=", "==", "in", "is_true")

# Canonical quantity for every spelling that has appeared in configs, pur_science outputs,
# prompts or pilot model answers. Value is (quantity, implied_operator_or_None).
_ALIASES: dict[str, tuple[str, str | None]] = {
    # MDI mass fraction of polyol + MDI
    "mdi_fraction": ("mdi_fraction", None),
    "mdi_fraction_min": ("mdi_fraction", ">="),
    "min_mdi_fraction": ("mdi_fraction", ">="),
    "mdi_fraction_lower_bound": ("mdi_fraction", ">="),
    "mdi_fraction_floor": ("mdi_fraction", ">="),
    "minimum_mdi_fraction": ("mdi_fraction", ">="),
    "mdi_fraction_max": ("mdi_fraction", "<="),
    "mdi_fraction_upper_bound": ("mdi_fraction", "<="),
    "mdi_fraction_of_polyol_plus_mdi": ("mdi_fraction", None),
    "mdi_mass_fraction": ("mdi_fraction", None),
    "mdi fraction": ("mdi_fraction", None),
    # stoichiometric ratio
    "nco_oh": ("nco_oh", None),
    "nco_oh_min": ("nco_oh", ">="),
    "nco_oh_max": ("nco_oh", "<="),
    "nco:oh": ("nco_oh", None),
    "nco_to_oh": ("nco_oh", None),
    # response windows
    "eta80_broad": ("eta80_broad", None),
    "eta80_broad_pa_s": ("eta80_broad", None),
    "eta80_preferred": ("eta80_preferred", None),
    "eta80_preferred_pa_s": ("eta80_preferred", None),
    "eta120_broad": ("eta120_broad", None),
    "eta120_broad_pa_s": ("eta120_broad", None),
    "eta120_preferred": ("eta120_preferred", None),
    "eta120_preferred_pa_s": ("eta120_preferred", None),
    "ratio_broad": ("ratio_broad", None),
    "ratio_preferred": ("ratio_preferred", None),
    # gates
    "chemistry_in_domain": ("chemistry_in_domain", "is_true"),
    "require_chemistry_in_domain": ("chemistry_in_domain", "is_true"),
    "interval_inside_broad": ("interval_inside_broad", "is_true"),
    "interval_inside_preferred": ("interval_inside_preferred", "is_true"),
    "domain_ratio_max": ("domain_ratio", "<="),
    "domain_ratio": ("domain_ratio", "<="),
    # explicit "nothing is binding"
    "none": ("none", None),
}

# Config key that owns the numeric bounds of each canonical quantity.
_BOUND_KEYS: dict[str, str] = {
    "mdi_fraction": "mdi_fraction_of_polyol_plus_mdi",
    "nco_oh": "nco_oh",
    "eta80_broad": "eta80_broad_pa_s",
    "eta80_preferred": "eta80_preferred_pa_s",
    "eta120_broad": "eta120_broad_pa_s",
    "eta120_preferred": "eta120_preferred_pa_s",
    "ratio_broad": "ratio_broad",
    "ratio_preferred": "ratio_preferred",
}


class OntologyError(ValueError):
    pass


def normalize_quantity(name: Any) -> tuple[str | None, str | None]:
    """Map any known spelling to (canonical_quantity, implied_operator).

    Unknown names return (None, None) rather than raising, so an unexpected model answer is
    scored as a schema failure instead of crashing the benchmark.
    """
    if name is None:
        return None, None
    key = str(name).strip().lower().replace("-", "_")
    if key in _ALIASES:
        return _ALIASES[key]
    key2 = key.replace(" ", "_")
    return _ALIASES.get(key2, (None, None))


def is_canonical_spelling(name: Any) -> bool:
    """True only when `name` is already the canonical quantity string itself."""
    quantity, _ = normalize_quantity(name)
    return quantity is not None and str(name).strip() == quantity


@dataclass(frozen=True)
class CanonicalConstraint:
    quantity: str
    operator: str | None = None
    threshold: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def canonical_constraint(
    name: Any,
    *,
    threshold: float | None = None,
    candidate_value: float | None = None,
    bounds: Any = None,
    operator: str | None = None,
) -> dict[str, Any]:
    """Build the canonical constraint object for a constraint name.

    The operator is taken from (1) an explicit argument, (2) the alias table, or (3) the
    observed geometry: a candidate below the lower bound makes the lower bound binding.
    """
    quantity, implied = normalize_quantity(name)
    if quantity is None:
        raise OntologyError(f"Unknown constraint name {name!r}; no canonical quantity is registered")
    op = operator or implied
    lo = hi = None
    if bounds is not None:
        try:
            lo, hi = [float(x) for x in bounds]
        except (TypeError, ValueError):
            lo = hi = None
    if op is None and candidate_value is not None and lo is not None and hi is not None:
        op = ">=" if float(candidate_value) < lo else "<="
    if threshold is None and lo is not None and hi is not None and op in (">=", "<="):
        threshold = lo if op == ">=" else hi
    return CanonicalConstraint(quantity=quantity, operator=op, threshold=None if threshold is None else float(threshold)).to_dict()


def constraint_bounds_for(config: dict[str, Any], quantity: str) -> list[float] | None:
    key = _BOUND_KEYS.get(quantity)
    if not key:
        return None
    bounds = (config.get("hard_constraints") or {}).get(key)
    return [float(x) for x in bounds] if bounds else None


def canonical_from_active_constraint(active: dict[str, Any] | None, config: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Canonicalise the `active_constraint` block produced by pur_science or an Agent."""
    if not active or not active.get("name"):
        return None
    quantity, _ = normalize_quantity(active.get("name"))
    bounds = constraint_bounds_for(config, quantity) if (config and quantity) else None
    try:
        return canonical_constraint(
            active.get("name"),
            threshold=active.get("threshold"),
            candidate_value=active.get("candidate_value"),
            bounds=bounds,
        )
    except OntologyError:
        return None


def same_constraint(a: Any, b: Any, *, require_operator: bool = False) -> bool:
    """Semantic equality of two constraint references.

    Accepts plain names or canonical objects. `mdi_fraction_min` and `mdi_fraction` are the
    same scientific constraint; only `schema_correctness` cares that they are spelled
    differently.
    """
    qa, oa = _as_quantity_operator(a)
    qb, ob = _as_quantity_operator(b)
    if qa is None or qb is None or qa != qb:
        return False
    if require_operator and oa is not None and ob is not None and oa != ob:
        return False
    return True


def _as_quantity_operator(value: Any) -> tuple[str | None, str | None]:
    if isinstance(value, dict):
        quantity = value.get("quantity") or value.get("name")
        q, implied = normalize_quantity(quantity)
        return q, (value.get("operator") or implied)
    return normalize_quantity(value)

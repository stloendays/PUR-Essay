from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any

SECRET_ENV_VARS = ("OPENAI_API_KEY",)
_KEY_PATTERN = re.compile(r"\b(sk-[A-Za-z0-9_\-]{8,})\b")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj: Any) -> str:
    return sha256_text(json.dumps(obj, sort_keys=True, default=str))


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def new_run_id(prefix: str = "run") -> str:
    return f"{prefix}_{_dt.datetime.now(_dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"


def scrub_secrets(obj: Any) -> Any:
    """Recursively replace any API-key-looking string or the live key value with a redaction marker."""
    live = [v for v in (os.getenv(k) for k in SECRET_ENV_VARS) if v]

    def fix(s: str) -> str:
        for v in live:
            if v and v in s:
                s = s.replace(v, "[REDACTED_API_KEY]")
        return _KEY_PATTERN.sub("[REDACTED_API_KEY]", s)

    if isinstance(obj, str):
        return fix(obj)
    if isinstance(obj, dict):
        return {k: scrub_secrets(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [scrub_secrets(v) for v in obj]
    return obj


def _json_default(x: Any) -> Any:
    if hasattr(x, "item"):
        return x.item()
    if hasattr(x, "to_dict"):
        return x.to_dict()
    if isinstance(x, Path):
        return str(x)
    return str(x)


def write_run_record(path: str | Path, record: dict[str, Any]) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = scrub_secrets(json.loads(json.dumps(record, default=_json_default)))
    path.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    return path


def build_run_record(
    *,
    run_id: str,
    benchmark_id: str,
    condition: str,
    provider: str,
    model: str,
    prompt_hash: str,
    data_hashes: dict[str, str],
    config_hash: str,
    anonymization_seed: int | None,
    llm_seed: int | None,
    tool_trace: list[dict[str, Any]],
    final_json: dict[str, Any] | None,
    raw_final_text: str,
    usage: dict[str, Any] | None,
    response_ids: list[str],
    latency_s: float,
    strategy_check: dict[str, Any] | None,
    error: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "timestamp_utc": utc_now(),
        "benchmark_id": benchmark_id,
        "condition": condition,
        "provider": provider,
        "model": model,
        "prompt_sha256": prompt_hash,
        "data_sha256": data_hashes,
        "config_sha256": config_hash,
        "anonymization_seed": anonymization_seed,
        "llm_seed": llm_seed,
        "tool_call_count": len(tool_trace),
        "tool_trace": tool_trace,
        "final_json": final_json,
        "raw_final_text": raw_final_text,
        "usage": usage,
        "api_response_ids": response_ids,
        "latency_s": latency_s,
        "strategy_check": strategy_check,
        "error": error,
        **(extra or {}),
    }

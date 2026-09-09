#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd

from pur_agent.config import load_json
from pur_agent.llm_client import OpenAIResponsesClient
from pur_agent.runtime import StrategyEnforcingExecutor
from pur_agent.tools import DecisionToolbox


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a < 0 or b <= a:
            raise
        return json.loads(text[a:b+1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind-dir", default="benchmark/recover_v1/blind")
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL"))
    ap.add_argument("--out", default="results/recover_v1/run_001.json")
    args = ap.parse_args()
    if not args.model:
        raise SystemExit("Set OPENAI_MODEL or pass --model")
    blind = Path(args.blind_dir)
    cfg = load_json(blind / "benchmark_config.json")
    df = pd.read_csv(blind / "candidates.csv")
    executor = StrategyEnforcingExecutor(DecisionToolbox(df, cfg))
    instructions = Path("prompts/recover_v1_system.txt").read_text(encoding="utf-8")
    task = (blind / "task.json").read_text(encoding="utf-8")
    client = OpenAIResponsesClient(args.model)
    text, meta = client.run(instructions=instructions, task=task, executor=executor)
    decision = _extract_json(text)
    payload = {
        "benchmark_id": cfg.get("benchmark_id"),
        "model": args.model,
        "decision": decision,
        "strategy_check": executor.strategy_check().__dict__,
        "api": meta,
    }
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

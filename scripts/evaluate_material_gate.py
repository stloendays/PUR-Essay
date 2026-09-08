#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pur_bridge import evaluate_material_gate

ap = argparse.ArgumentParser()
ap.add_argument("csv", help="Material audit CSV following data/material_equivalence_template.csv")
args = ap.parse_args()
r = evaluate_material_gate(args.csv)
print(f"{r.state}: {r.reason}")

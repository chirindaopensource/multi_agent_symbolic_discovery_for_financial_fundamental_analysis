"""Compare Task 27's MAPE tables of two smoke runs.

Usage: python verification/compare_task27.py RUN_A RUN_B [--seed 11] [--atol 1e-9]
"""
import argparse
from pathlib import Path

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("run_a")
parser.add_argument("run_b")
parser.add_argument("--seed", default="11")
parser.add_argument("--atol", type=float, default=1e-9)
args = parser.parse_args()
relative = Path("task_27") / f"seed_{args.seed}" / "mape_variants_task_27.csv"
a = pd.read_csv(Path(args.run_a).expanduser() / relative).set_index(["model", "market"]).sort_index()
b = pd.read_csv(Path(args.run_b).expanduser() / relative).set_index(["model", "market"]).sort_index()
print("rows only in A:", sorted(set(a.index) - set(b.index)))
print("rows only in B:", sorted(set(b.index) - set(a.index)))
shared = a.index.intersection(b.index)
for column in ("pooled", "common_pooled", "n_scored", "n_common"):
    difference = (a.loc[shared, column] - b.loc[shared, column]).abs()
    changed = difference[difference > args.atol]
    print(f"{column}: {len(changed)} of {len(shared)} rows differ by more than {args.atol}")
    if len(changed):
        pair = pd.concat([a.loc[changed.index, column], b.loc[changed.index, column]], axis=1, keys=["A", "B"])
        print(pair.to_string())

"""Issue I: Task 21 must halt only on infeasibility, never on a feasible start SLSQP marks unsuccessful.

Sixty seeded cells with near-zero prices, outliers and two near-identical perspectives. Before the
fix, 3 of the 60 cells halt although several of their starts are feasible; after it, none may halt.
Usage: python verification/check_task21_solver.py [--expect-halts N]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from notebook_namespace import load_namespace  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--expect-halts", type=int, default=0)
args = parser.parse_args()
ns = load_namespace(ROOT)
fit = ns["fit_perspective_weights_task_21"]
config = ns["build_solver_config_task_21"]()
rng = np.random.default_rng(0)
halts, unsuccessful_chosen = 0, 0
for unit in range(60):
    n = int(rng.integers(200, 600))
    y = rng.lognormal(3.0, 1.0, n)
    bias, scale = rng.normal(0, 0.3, 5), rng.uniform(0.1, 0.8, 5)
    x = y[:, None] * np.exp(bias + rng.normal(0, 1, (n, 5)) * scale)
    x[:, 1] = x[:, 0] * 1.0000001
    x[rng.integers(0, n, 5), 2] *= 1e4
    y[rng.integers(0, n, 3)] = 1e-3
    try:
        result = fit(x, y, config, 8, unit)
    except RuntimeError as error:
        halts += 1
        print(f"unit {unit}: HALT: {str(error)[:200]}")
        continue
    weights = np.asarray(result["weights"], dtype=float)
    assert abs(weights.sum() - 1.0) <= 1e-12 and weights.min() >= 0.0, unit
    assert result["equality_violation"] <= config["feasibility_tol"], unit
    chosen = result["per_start"][result["chosen_start"]]
    unsuccessful_chosen += int(not chosen["success"])
print(f"halts={halts} chosen_unsuccessful_but_feasible={unsuccessful_chosen}")
assert halts == args.expect_halts, f"expected {args.expect_halts} halts, observed {halts}"
print("CHECK OK")

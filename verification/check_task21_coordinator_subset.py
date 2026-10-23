"""Issue A.1: Task 21 must fit over the meta-coordinator's subset A*, from the coordinator's proposal.

Two markets, one sector, Bull and Bear regimes, five perspectives, 320 training rows per cell and a
held-out window. The proposal for S1|Bull zeroes three perspectives; S1|Bear has no proposal. A second
run gives S1|Bull a one-perspective proposal, which is not a valid selection.
Usage: python verification/check_task21_coordinator_subset.py
"""
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from notebook_namespace import load_namespace  # noqa: E402

ns = load_namespace(ROOT)
run_task_21 = ns["run_task_21"]
separator = ns["MARKET_CELL_SEPARATOR_TASK_21"]
perspectives = ["earnings", "cashflow", "asset", "growth", "quality"]
rng = np.random.default_rng(7)

# Build the long predictions frame in the column layout _stage_task_21 passes.
rows = []
for market in ("M1", "M2"):
    for quarter_index in range(40):
        quarter = f"{2000 + quarter_index // 4}Q{quarter_index % 4 + 1}"
        partition = "train" if quarter_index < 32 else "test"
        regime = "Bull" if quarter_index % 2 == 0 else "Bear"
        for firm in range(20):
            target = float(rng.lognormal(3.0, 0.5))
            for position, name in enumerate(perspectives):
                prediction = target * float(np.exp(rng.normal(0.05 * position, 0.2 + 0.05 * position)))
                rows.append({
                    "perspective": name, "market": market, "quarter": quarter, "firm_id": f"{market}_F{firm}",
                    "partition": partition, "context_key": f"S1|{regime}", "target": target,
                    "prediction": prediction,
                })
frame = pd.DataFrame(rows)
training_rows = frame.loc[(frame["partition"] == "train") & (frame["perspective"] == "earnings")]
assert training_rows.groupby(["market", "context_key"]).size().min() >= 250

# A proposal over S1|Bull that selects earnings and quality only; S1|Bear carries no proposal.
proposals = {"S1|Bull": {"weights": {"earnings": 0.6, "cashflow": 0.0, "asset": 0.0, "growth": 0.0, "quality": 0.4}}}
with tempfile.TemporaryDirectory() as directory:
    result = run_task_21(frame, directory, perspectives=perspectives, seed=0, coordinator_proposals=proposals)
matrix = result["weight_matrix"]
for market in ("M1", "M2"):
    bull = matrix.loc[(market, "S1", "Bull"), perspectives].to_numpy(dtype=float)
    assert np.all(bull[[1, 2, 3]] == 0.0), (market, bull)
    assert abs(float(bull.sum()) - 1.0) <= 1e-12, (market, bull)
    bull_fit = result["fits"][f"{market}{separator}S1|Bull"]
    assert bull_fit["initial_point_source"] == "coordinator_proposal", bull_fit["initial_point_source"]
    assert bull_fit["support"] == [True, False, False, False, True], bull_fit["support"]
    bear_fit = result["fits"][f"{market}{separator}S1|Bear"]
    assert bear_fit["support"] == [True] * 5, bear_fit["support"]
    assert bear_fit["initial_point_source"] == "uniform", bear_fit["initial_point_source"]
    print(market, "S1|Bull weights", np.round(bull, 6), "S1|Bear weights",
          np.round(matrix.loc[(market, "S1", "Bear"), perspectives].to_numpy(dtype=float), 6))
assert result["weights_mechanism"] == "coordinator_subset_slsqp", result["weights_mechanism"]
assert result["n_units_with_proposal"] == 2, result["n_units_with_proposal"]
assert result["proposal_support_too_small"] == [], result["proposal_support_too_small"]
assert int(result["heldout_predictions"]["prediction"].notna().sum()) == len(result["heldout_predictions"])

# A one-perspective proposal is not a valid selection: the unit is fitted over every perspective.
single = {f"M1{separator}S1|Bull": {"earnings": 1.0, "cashflow": 0.0, "asset": 0.0, "growth": 0.0, "quality": 0.0}}
with tempfile.TemporaryDirectory() as directory:
    second = run_task_21(frame, directory, perspectives=perspectives, seed=0, coordinator_proposals=single)
assert second["proposal_support_too_small"] == [f"M1{separator}S1|Bull"], second["proposal_support_too_small"]
assert second["fits"][f"M1{separator}S1|Bull"]["support"] == [True] * 5
assert second["fits"][f"M1{separator}S1|Bull"]["initial_point_source"] == "uniform"
assert second["weights_mechanism"] == "full_simplex_slsqp", second["weights_mechanism"]

# Without proposals the fit is the full-simplex fit from the uniform point.
with tempfile.TemporaryDirectory() as directory:
    third = run_task_21(frame, directory, perspectives=perspectives, seed=0)
assert third["weights_mechanism"] == "full_simplex_slsqp" and third["n_units_with_proposal"] == 0
assert all(fit["support"] == [True] * 5 and fit["initial_point_source"] == "uniform" for fit in third["fits"].values())
print("CHECK OK")

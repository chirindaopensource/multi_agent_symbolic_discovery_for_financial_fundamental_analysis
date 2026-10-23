"""Issue A.2: the meta-coordinator (Task 20) must run per market, its contexts being (market, sector, regime).

Two markets whose best perspective differs: in market X the earnings perspective is near-exact, in market Y
the asset perspective is. The Task 22 stage adapter must return distinct per-market rows labelled X::... and
Y::..., market-labelled proposals and learnings, and one Task 20 artefact directory per market.
Usage: python verification/check_task20_per_market.py
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
stage_task_20 = ns["_stage_task_20"]
separator = ns["MARKET_CELL_SEPARATOR_TASK_21"]
perspectives = ["earnings", "cashflow", "asset", "growth", "quality"]
best_of_market = {"X": "earnings", "Y": "asset"}
rng = np.random.default_rng(3)

# Build the long predictions frame in the column layout the stage receives.
rows = []
for market, best in best_of_market.items():
    for quarter_index in range(40):
        quarter = f"{2000 + quarter_index // 4}Q{quarter_index % 4 + 1}"
        partition = "train" if quarter_index < 32 else "test"
        regime = "Bull" if quarter_index % 2 == 0 else "Bear"
        for firm in range(20):
            target = float(rng.lognormal(3.0, 0.5))
            for name in perspectives:
                noise = 0.01 if name == best else 0.6
                rows.append({
                    "perspective": name, "market": market, "quarter": quarter, "firm_id": f"{market}_F{firm}",
                    "partition": partition, "context_key": f"S1|{regime}", "target": target,
                    "prediction": target * float(np.exp(rng.normal(0.0, noise))),
                })
frame = pd.DataFrame(rows)
services = ns["standin_services_task_36"]()
with tempfile.TemporaryDirectory() as directory:
    context = {
        "settings": {
            "perspectives": perspectives, "coordinator_iterations": 3, "min_firm_quarters": 200,
            "generator": "model", "allow_stand_in": False,
        },
        "work_dir": directory, "seed": 11, "services": services, "perspective_predictions": frame,
        "role_callables": services["role_callables"], "run_id": "check_a2",
    }
    outputs = stage_task_20(context)
    market_dirs = sorted(path.name for path in (Path(directory) / "task_20").iterdir() if path.is_dir())
    assert market_dirs == ["X", "Y"], market_dirs
    for market in ("X", "Y"):
        assert (Path(directory) / "task_20" / market / "per_cell_proposals.json").is_file(), market
weights = outputs["coordinator_weights"]
labels = [str(label) for label in weights.index]
assert sorted(labels) == [f"{m}{separator}S1|{r}" for m in ("X", "Y") for r in ("Bear", "Bull")], labels
for label in labels:
    market = label.split(separator, 1)[0]
    row = weights.loc[label, perspectives].to_numpy(dtype=float)
    best = best_of_market[market]
    assert perspectives[int(np.argmax(row))] == best, (label, np.round(row, 4))
    print(label, dict(zip(perspectives, np.round(row, 4))))
x_row = weights.loc[f"X{separator}S1|Bull", perspectives].to_numpy(dtype=float)
y_row = weights.loc[f"Y{separator}S1|Bull", perspectives].to_numpy(dtype=float)
assert not np.allclose(x_row, y_row), "the two markets must receive distinct coordinator rows"
assert all(separator in key and key.split(separator, 1)[0] in ("X", "Y") for key in outputs["coordinator_proposals"])
assert all(f"{market}{separator}S1|Bull" in outputs["coordinator_proposals"] for market in ("X", "Y"))
assert all(key.split(separator, 1)[0] in ("X", "Y") for key in outputs["meta_learnings"]), outputs["meta_learnings"]

# A sector pool with enough firm-quarters but too few complete rows escalates to the market pool; every unit
# the coordinator attempted must still publish a proposal, the escalated one carrying its pool's.
escalating = frame.loc[frame["market"] == "X"].copy()
escalating.loc[escalating["firm_id"].isin([f"X_F{firm}" for firm in range(10)]), "context_key"] = (
    escalating["context_key"].str.replace("S1", "S2", regex=False)
)
blank = (escalating["perspective"] == "growth") & escalating["context_key"].str.startswith("S2") & (
    escalating["quarter"].str.slice(0, 4).astype(int) < 2004
)
escalating.loc[blank, "prediction"] = np.nan
with tempfile.TemporaryDirectory() as directory:
    run = ns["run_task_20"](
        escalating, directory, 5, 3, 200, 11, role_callables=services["role_callables"],
        tokenizer=services["tokenizer"], perspectives=perspectives, run_id="check_a2_escalation",
    )
units = run["per_unit_proposals"]
assert "S2|POOLED" in units and units["S2|POOLED"]["pool_key"] == ns["POOL_ALL"], units.get("S2|POOLED")
assert units[ns["POOL_ALL"]]["pool_key"] is None
assert units["S2|POOLED"]["weights"] == units[ns["POOL_ALL"]]["weights"]
print("escalated unit S2|POOLED carries the market pool's proposal:", units["S2|POOLED"]["pool_key"])
print("CHECK OK")

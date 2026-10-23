"""Issue F: the EV/EBIT and EV/EBITDA baselines must bridge enterprise value per share to the share price.

Hand-checkable fixture: EBIT_ps = 10, median EV/EBIT = 12, debt = 300, cash = 100, shares = 10, FX = 1, so the
price is 120 - 20 = 100. A row without cash has a missing price; a row whose net debt per share exceeds its
enterprise value per share has a missing price that is counted; a row with FX = 2 nets 40 per share.
Usage: python verification/check_task25_ev_bridge.py
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from notebook_namespace import load_namespace  # noqa: E402

ns = load_namespace(ROOT)
stage = ns["sector_median_baselines_task_25"]
frame = pd.DataFrame(
    {
        "SECTOR_MEDIAN_PE": [15.0, 15.0, 15.0, 15.0],
        "EPS_TTM": [5.0, 5.0, 5.0, 5.0],
        "SECTOR_MEDIAN_EV_EBIT": [12.0, 12.0, 12.0, 12.0],
        "EBIT_ps": [10.0, 10.0, 10.0, 10.0],
        "SECTOR_MEDIAN_EV_EBITDA": [8.0, 8.0, 8.0, 8.0],
        "EBITDA_ps": [20.0, 20.0, 20.0, 20.0],
        "SECTOR_MEDIAN_P_BOOK": [2.0, 2.0, 2.0, 2.0],
        "BVPS": [30.0, 30.0, 30.0, 30.0],
        ns["BRIDGE_TOTAL_DEBT_COLUMN"]: [300.0, 300.0, 3000.0, 300.0],
        ns["BRIDGE_CASH_COLUMN"]: [100.0, np.nan, 100.0, 100.0],
        ns["BRIDGE_SHARES_COLUMN"]: [10.0, 10.0, 10.0, 10.0],
        ns["FX_RATE_COLUMN"]: [1.0, 1.0, 1.0, 2.0],
    },
    index=["hand", "missing_cash", "negative", "fx_two"],
)
warnings = []
result = stage(frame, warnings)
print(result.to_string())
assert result.loc["hand", "ev_ebit_baseline"] == 100.0, result.loc["hand", "ev_ebit_baseline"]
assert result.loc["hand", "ev_ebitda_baseline"] == 160.0 - 20.0
assert math.isnan(result.loc["missing_cash", "ev_ebit_baseline"])
assert math.isnan(result.loc["negative", "ev_ebit_baseline"])
assert result.loc["fx_two", "ev_ebit_baseline"] == 120.0 - 40.0
assert (result["pe_baseline"] == 75.0).all() and (result["pb_baseline"] == 60.0).all()
counts = result.attrs[ns["EV_BRIDGE_COUNTS_ATTR"]]
assert counts["ev_ebit_baseline"] == {"n_bridge_missing": 1, "n_non_positive": 1}, counts
assert counts["ev_ebitda_baseline"] == {"n_bridge_missing": 1, "n_non_positive": 1}, counts
assert any("cash input" in text for text in warnings) and any("non-positive price" in text for text in warnings)
try:
    stage(frame.assign(**{ns["FX_RATE_COLUMN"]: [1.0, 0.0, 1.0, 1.0]}), [])
except ValueError:
    pass
else:
    raise AssertionError("a non-positive FX rate must halt")
print("CHECK OK")

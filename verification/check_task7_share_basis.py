"""Issue D: Task 7 must detect a share-basis break between quarter t and t+1 in the forward target.

Three issuers over four quarters: (i) a contemporaneous 2-for-1 split (reference date = each period end),
(ii) the same split under one snapshot reference date, (iii) a 10 % buyback. Under "drop" only (i) is
flagged and its target dropped; under "adjust" (iv) its target is the successor price times 2.
Usage: python verification/check_task7_share_basis.py
"""
import math
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "verification"))
from notebook_namespace import load_namespace  # noqa: E402

ns = load_namespace(ROOT)
build = ns["build_forward_target_task_7"]
target_column = ns["TARGET_COLUMN"]
attr = ns["SHARE_BASIS_AUDIT_ATTR_TASK_7"]
period_ends = pd.to_datetime(["2020-03-31", "2020-06-30", "2020-09-30", "2020-12-31"])
snapshot = pd.Timestamp("2021-03-01")
issuers = {
    "A_contemporaneous_split": ([100.0, 100.0, 200.0, 200.0], [50.0, 52.0, 26.0, 27.0], "contemporaneous"),
    "B_snapshot_split": ([100.0, 100.0, 200.0, 200.0], [50.0, 52.0, 26.0, 27.0], "snapshot"),
    "C_buyback": ([100.0, 90.0, 90.0, 90.0], [50.0, 55.0, 55.0, 56.0], "contemporaneous"),
}
rows = []
for issuer, (shares, prices, basis) in issuers.items():
    for quarter, period_end in enumerate(period_ends):
        rows.append({
            "issuer_id": issuer, "fiscal_quarter_label": f"2020Q{quarter + 1}", "fiscal_period_end": period_end,
            "filing_date_original": period_end + pd.Timedelta(days=40), "px_close_period_end": prices[quarter],
            "bs_shares_outstanding": shares[quarter],
            "px_split_adjustment_reference_date": period_end if basis == "contemporaneous" else snapshot,
        })
panel = pd.DataFrame(rows)


def target_of(frame: pd.DataFrame, issuer: str, quarter: int) -> float:
    """Read one row's forward target."""
    mask = (frame["issuer_id"] == issuer) & (frame["fiscal_quarter_label"] == f"2020Q{quarter}")
    return float(frame.loc[mask, target_column].iloc[0])


dropped = build(panel, share_basis_policy="drop")
ledger = dropped.attrs[attr]
print(ledger.to_string(index=False))
assert list(ledger["issuer_id"]) == ["A_contemporaneous_split"], list(ledger["issuer_id"])
assert pd.Timestamp(ledger["fiscal_period_end"].iloc[0]) == pd.Timestamp("2020-06-30")
assert float(ledger["share_ratio"].iloc[0]) == 2.0 and float(ledger["cap_ratio"].iloc[0]) == 1.0
assert list(ledger["action"]) == ["target_dropped"]
assert math.isnan(target_of(dropped, "A_contemporaneous_split", 2))
assert target_of(dropped, "A_contemporaneous_split", 1) == 52.0
assert target_of(dropped, "A_contemporaneous_split", 3) == 27.0
assert target_of(dropped, "B_snapshot_split", 2) == 26.0
assert target_of(dropped, "C_buyback", 1) == 55.0
assert all(math.isnan(target_of(dropped, issuer, 4)) for issuer in issuers)
row = dropped.loc[(dropped["issuer_id"] == "A_contemporaneous_split") & (dropped["fiscal_quarter_label"] == "2020Q2")]
assert row[ns["TARGET_DATE_REALISED_COLUMN_TASK_7"]].isna().all()

adjusted = build(panel, share_basis_policy="adjust")
assert target_of(adjusted, "A_contemporaneous_split", 2) == 26.0 * 2.0, target_of(adjusted, "A_contemporaneous_split", 2)
assert target_of(adjusted, "B_snapshot_split", 2) == 26.0
assert len(adjusted.attrs[attr]) == 1 and adjusted.attrs[attr]["action"].iloc[0].startswith("target_multiplied_by_2")
try:
    build(panel, share_basis_policy="clip")
except ValueError as error:
    assert "HALT" in str(error)
else:
    raise AssertionError("an undeclared policy must halt")
print("CHECK OK")

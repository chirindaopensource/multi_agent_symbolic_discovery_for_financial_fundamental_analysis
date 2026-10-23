## **Usage Example**

This guide demonstrates the study interface `run_task_36` of the Python reproduction of *Self-Evolving Multi-Agent Symbolic Discovery for Financial Fundamental Analysis* (Kelvin J.L. Koa), the hierarchical multi-agent framework **MUFASA** (Multi-Agent Fundamental Analysis with Symbolic Adaptive learning). Python implementation author: **CS Chirinda**.

The example proceeds in four steps. Step 1 fabricates the five raw panels the driver ingests: `fundamental_quarter` (L1, Bloomberg-style), `macro_quarter` (L2, FactSet-style), `index_daily` (L3, Yahoo-style), `index_membership` (L4a) and `classifications`. Step 2 reads the existing `config.yaml` into the plain dictionary `config` and conforms the firm panel to the schema that file declares. Step 3 composes every argument of `run_task_36`. Step 4 calls the interface and reads back its three institutional assets: the fitted closed-form equations, the context-indexed weight matrix and the per-hypothesis reliability profiles. Every code fence below was executed, in the order shown, against `multi_agent_symbolic_discovery_for_financial_fundamental_analysis_draft.ipynb`; the section **Verification record** states exactly what ran and what did not.

**Assumptions and execution requirements.**

1. Every research callable and helper already lives in the **single Jupyter notebook** `multi_agent_symbolic_discovery_for_financial_fundamental_analysis_draft.ipynb`, the project's official notebook. Execute its code cells in order, from the import cell under the heading *Import Essential Modules* through the cell headed **Task 36: Top-Level Pipeline Orchestrator**. Do **not** execute the notebook's own closing cells *Study Assembly* and *Study Execution*: they start a separate study run. Then append the example cells below. **No Python task-module folder (`.py` package) is imported or required**; every notebook name the example uses (`run_task_36`, `RAW_PANELS_TASK_36`, `STUDY_STATUSES_TASK_36`, `DATA_MODES_TASK_36`, `Task36NotCompletedError`, `collect_provenance_task_36`, `build_environment_task_36`, `STUDY_ENVIRONMENT_DECLARATION`, `standin_services_task_36` and `run_task_1` … `run_task_35`) is resolved from that notebook's global namespace.
2. The working directory is the notebook's folder, and `config.yaml` already exists there. The example reads it and never modifies it. Its JSON twin, `study_config.json`, carries the same parameters and is what the notebook's *licensed* loader reads; this example uses the YAML file.
3. The verification interpreter was Python 3.13.9 with NumPy 2.3.5, pandas 2.3.3 and PyYAML 6.0.3. The example-specific imports are NumPy, pandas and **PyYAML**.
4. **Faker is not used.** The panels come from a private, seeded NumPy `PCG64` data-generating process (seed `20261023`), the functionally equivalent alternative the brief permits. Company names are built from a fixed stem list, and ISIN, CUSIP and SEDOL identifiers carry valid check digits, so no live security is impersonated by chance and every run is bit-for-bit reproducible.
5. **Every value is synthetic.** Statements, prices, yields, index levels and memberships are artificial. A completed run on these panels earns the published status `pipeline_verified_on_synthetic_data`, never `study_complete`; it demonstrates the input contract and the wiring of the 35 stages, not the paper's empirical results.
6. On Windows, keep the output directory short (the example uses `~/mufasa_runs`). Tasks 30–34 nest complete pipeline runs inside the output tree, and Windows refuses paths longer than 260 characters unless long paths are enabled.
7. All date columns are `datetime64[ns]`. A column at `datetime64[s]` (pandas' default for some constructors) makes Task 6's as-of join raise `MergeError`.

### **The study interface: `run_task_36`**

The actual signature, read from the notebook, is:

```text
run_task_36(
    config: Mapping[str, Any],
    panels: Mapping[str, pd.DataFrame],
    output_dir: Union[str, os.PathLike[str]],
    *,
    registry: Optional[Mapping[int, Callable[..., Any]]] = None,
    seeds: Sequence[int],
    services: Optional[Mapping[str, Any]] = None,
    skip: Sequence[int] = (),
    data_mode: str = "licensed",
    resume: bool = True,
) -> Dict[str, Any]
```

Three arguments are positional; everything after `*` is keyword-only. `seeds` is keyword-only **and has no default**, so it must always be passed.

| Argument | Default | Contract |
| --- | --- | --- |
| `config` | required | The full configuration mapping: the twelve operational blocks of `config.yaml` (`validation`, `market_structure`, `cleaning`, `macro`, `pipeline`, `baselines`, `evaluation`, `ablation`, `memory_ablation`, `sensitivity`, `robustness`, `packaging`), the verbatim `study_specification`, **plus** an `environment` block that is measured at run time (Step 3), never stored in the file. The `pipeline` block rejects unknown keys. |
| `panels` | required | Exactly the five DataFrames named by `RAW_PANELS_TASK_36`: `fundamental_quarter`, `macro_quarter`, `index_daily`, `index_membership`, `classifications`. A missing or extra panel raises `ValueError`. |
| `output_dir` | required | The run's directory. It receives one `task_NN` folder per stage, `driver_checkpoints`, the manifest and, when needed, the failure ledger. |
| `registry` | `None` | The orchestrators keyed by task number, `{1: run_task_1, …, 35: run_task_35}`. The default `None` is rejected as a malformed registry, so in practice the argument is required. |
| `seeds` | none (required) | Non-empty, distinct integer seeds. `config.yaml` declares `study_specification.reproducibility.seed_values = [11, 23, 41, 67, 101]`, identical to the notebook constant `STUDY_SEED_LIST`. Task 22 runs the whole MUFASA pipeline once per seed. |
| `services` | `None` (empty mapping) | Handles to the external services: `embed_fn` (sentence encoder), `tokenizer`, `role_callables` (the agent roles), `llm_client`, `funsearch_client`, `llm_sr_client`. With no service the LLM-driven stages cannot run; `standin_services_task_36()` supplies the notebook's declared deterministic stand-ins for a synthetic verification. |
| `skip` | `()` | Driver stages declared skipped in advance. Only driver stages (1–4 and 22–35) may be named, and skipping a stage obliges you to skip its transitive consumers: skipping any of 30–34 also requires 35. |
| `data_mode` | `"licensed"` | One of `DATA_MODES_TASK_36 = ("licensed", "synthetic")`. It determines the published study status, and it must be `"synthetic"` for these panels. |
| `resume` | `True` | A driver stage whose checkpoint in `driver_checkpoints` matches its inputs is reloaded instead of recomputed. |

**Stage roles.** The plan holds 35 stages. The driver calls stages 1–4 and 22–35 directly. Stages 5–12, 15, 20 and 21 execute inside Task 22 (the per-seed MUFASA run), and stages 13, 14 and 16–19 are collaborators of Task 15. Every stage, however it was reached, returns one record.

**Return value.** A dictionary with the keys `status`, `records`, `outputs`, `order`, `manifest_path`, `failure_ledger_path`, `run_id`, `data_mode`, `skipped`, `loader_mode` and `seeds`. Each record carries `task`, `callable`, `role`, `status`, `n_calls`, `seconds`, `reason`, `root_cause`, `error_type`, `inputs_digest`, `call_keys`, `mode` and `stored`. `outputs[22]["runs"][seed]` is a `MufasaRunArtifacts` object whose fields are `run_id`, `aggregated_predictions`, `perspective_predictions`, `fitted_expressions`, `weight_matrix`, `distilled_learnings`, `reliability_profiles`, `missing_aggregate_counts`, `provenance` and `seed`.

**Status.** The driver decides one of three statuses:

| Driver `status` | Meaning | Published status (`STUDY_STATUSES_TASK_36`), licensed / synthetic |
| --- | --- | --- |
| `completed` | Every stage completed. | `study_complete` / `pipeline_verified_on_synthetic_data` |
| `completed_with_declared_skips` | Every stage not declared skipped completed. | `study_incomplete_with_declared_skips` / `pipeline_partially_verified_on_synthetic_data` |
| `not_completed` | At least one stage failed or was blocked by a failure. | none: the driver writes the manifest and the failure ledger, then raises `Task36NotCompletedError`, whose `.result` holds the full return mapping. |

### **Step 1: Synthetic Data Generation (the five raw panels)**

The data-generating process is built to pass the same validators that a vendor extract must pass, so every structural property the stages rely on is reproduced deliberately:

* **Universe.** Five markets (S&P 500, Russell 2000, STOXX 600, FTSE Asia Pacific ex-Japan, CSI 300). Each holds four GICS sectors of six firms, i.e. 24 live constituents per market-quarter. Six firms per sector keeps every sector-quarter cell above `cleaning.min_firms_per_sector_quarter = 5`, which the cross-sectional standardisation of Task 15 requires. Over 48 quarters (2012Q1–2023Q4) this gives 5,760 firm-quarters and 125 issuers, the extra five being the entrants that replace one delisted, acquired or market-cap-removed firm per market.
* **Accounting identities.** Trailing-twelve-month (TTM) flows are true sums of four quarterly flows, total assets equal liabilities plus equity, and free cash flow equals operating cash flow less capital expenditure.
* **Prices and the target.** The period-end price is TTM EPS times a sector P/E times a persistent sentiment factor, so valuation has learnable structure. `target` is the next quarter's market capitalisation, shifted forward within each issuer, and is missing on each issuer's last quarter (125 rows).
* **Structural zeros.** Banks, insurers, real-estate and similar industry groups (GICS 4010, 4030, 5510, 6010) report no cost of revenue or R&D, exactly as vendors leave those fields empty; `n_missing_fields` counts them (0.53 per row on average).
* **Calendar-aligned fiscal labels.** `FISCAL_LABEL_STYLE = "calendar"` writes `fiscal_quarter_label` as `"2012Q1"` on calendar fiscal years. The generator also implements the vendor style (`FISCAL_LABEL_STYLE = "vendor"`: `"FY2020Q2"` labels, June filers and one fiscal-year change), which also completes the pipeline. Every stage keys quarters on the calendar quarter, never on the label's text (see **Corrections made to the notebook**).

| Panel | Shape | Keys and content |
| --- | --- | --- |
| `fundamental_quarter` (L1) | 5,760 × 79 | Identifiers (`issuer_id`, ISIN, CUSIP, SEDOL, ticker), currencies and FX, GICS codes, fiscal calendar and filing dates, restatement flags, 15 quarterly and 14 TTM income and cash-flow items, 14 balance-sheet items with their conventions, price, market capitalisation, `bs_shares_diluted`, `enterprise_value`, `market`, `target`, `target_date`, `n_missing_fields`. |
| `macro_quarter` (L2) | 265 × 30 | One row per market and calendar quarter (2011Q1–2024Q1): the US, German, UK and Chinese curves, credit spreads, VIX, FX and commodity indices, plus the market's local 30-year yield, inflation, activity, the 30y–3m term spread and the real 10-year yield, with publication dates and vintages. |
| `index_daily` (L3) | 19,879 × 12 | Daily OHLC, adjusted close and volume for `^GSPC`, `^RUT`, `^STOXX`, `^FTAPXJ` and `000300.SS` from 2009-01-02 to 2024-03-29, drawn as Brownian bridges through historical anchor levels. `^FTAPXJ` carries `ticker_verified = False` because its Yahoo symbol is not confirmed. |
| `index_membership` (L4a) | 125 × 8 | Entry and exit dates per issuer and index, with exit reasons and the methodology version. `index_name` values equal the keys of `config["pipeline"]["index_to_market"]`. |
| `classifications` | 127 × 4 | GICS sector history per issuer with effective dates, including two reclassifications. This fifth panel is required by `RAW_PANELS_TASK_36`. |

#### **Step 1.1: Imports and data-generating constants**

```python
# ==============================================================================
# Step 1 — synthetic raw panels for run_task_36
# ==============================================================================
# Import postponed evaluation of annotations, as the notebook's import cell does.
from __future__ import annotations

# Import deepcopy so the loaded configuration is never mutated in place.
import copy

# Import Path for the output directory.
from pathlib import Path

# Import the typing names used in the signatures below.
from typing import Any, Dict, List, Mapping, Sequence, Tuple

# Import NumPy for the seeded PCG64 data-generating process.
import numpy as np

# Import pandas for the five raw DataFrames.
import pandas as pd

# Import PyYAML to read config.yaml.
import yaml

# Fix the seed of the data-generating process, so every panel is reproducible.
DGP_SEED: int = 20261023
# Fix the snapshot date of the synthetic vendor extracts.
EXTRACT_DATE: pd.Timestamp = pd.Timestamp("2024-03-29")
# Fix the first and last calendar quarter of the firm panel (2011 is TTM warm-up).
PANEL_FIRST_QUARTER: str = "2012Q1"
# Fix the last calendar quarter of the firm panel.
PANEL_LAST_QUARTER: str = "2023Q4"
# Fix the fiscal-label style: "calendar" writes "YYYYQn" labels on calendar fiscal years; "vendor"
# writes "FY2019Q3" labels with June filers and one fiscal-year change. Both complete the pipeline.
FISCAL_LABEL_STYLE: str = "calendar"

# Fix the constituents per (market, sector): config.yaml requires >= 5 firms per sector-quarter
# (pipeline.min_firms_per_sector_quarter) before Task 9 publishes a sector median.
FIRMS_PER_SECTOR: int = 6

# Fix the four GICS sectors of each synthetic universe (all eleven are represented overall).
MARKET_SECTORS: Dict[str, Tuple[str, ...]] = {
    "SP500": ("Information Technology", "Health Care", "Financials", "Industrials"),
    "RUSSELL2000": ("Industrials", "Health Care", "Consumer Discretionary", "Financials"),
    "STOXX600": ("Financials", "Industrials", "Consumer Staples", "Utilities"),
    "FTSE_APAC_EX_JP": ("Financials", "Information Technology", "Real Estate", "Materials"),
    "CSI300": ("Financials", "Industrials", "Consumer Staples", "Energy"),
}

# Fix the constituents per market at the panel start.
FIRMS_PER_MARKET: int = FIRMS_PER_SECTOR * 4

# Map each market label of config.yaml to its index name, ticker, currency and calendar.
MARKETS: Dict[str, Dict[str, str]] = {
    "SP500": {
        "index_name": "S&P 500",
        "ticker": "^GSPC",
        "currency": "USD",
        "calendar": "XNYS",
        "country": "US",
        "suffix": "US",
    },
    "RUSSELL2000": {
        "index_name": "Russell 2000",
        "ticker": "^RUT",
        "currency": "USD",
        "calendar": "XNYS",
        "country": "US",
        "suffix": "US",
    },
    "STOXX600": {
        "index_name": "STOXX 600",
        "ticker": "^STOXX",
        "currency": "EUR",
        "calendar": "XETR",
        "country": "DE",
        "suffix": "GY",
    },
    "FTSE_APAC_EX_JP": {
        "index_name": "FTSE Asia Pacific ex-Japan",
        "ticker": "^FTAPXJ",
        "currency": "USD",
        "calendar": "XHKG",
        "country": "HK",
        "suffix": "HK",
    },
    "CSI300": {
        "index_name": "CSI 300",
        "ticker": "000300.SS",
        "currency": "CNY",
        "calendar": "XSHG",
        "country": "CN",
        "suffix": "CH",
    },
}

# Map each GICS sector name to its two-digit code and representative industry groups.
GICS: Dict[str, Tuple[str, Tuple[Tuple[str, str], ...]]] = {
    "Energy": ("10", (("1010", "Energy"),)),
    "Materials": ("15", (("1510", "Materials"),)),
    "Industrials": ("20", (("2010", "Capital Goods"), ("2030", "Transportation"))),
    "Consumer Discretionary": (
        "25",
        (
            ("2510", "Automobiles & Components"),
            ("2550", "Consumer Discretionary Distribution & Retail"),
        ),
    ),
    "Consumer Staples": ("30", (("3020", "Food, Beverage & Tobacco"),)),
    "Health Care": (
        "35",
        (
            ("3510", "Health Care Equipment & Services"),
            ("3520", "Pharmaceuticals, Biotechnology & Life Sciences"),
        ),
    ),
    "Financials": ("40", (("4010", "Banks"), ("4030", "Insurance"))),
    "Information Technology": (
        "45",
        (("4510", "Software & Services"), ("4520", "Technology Hardware & Equipment")),
    ),
    "Communication Services": (
        "50",
        (("5010", "Telecommunication Services"), ("5020", "Media & Entertainment")),
    ),
    "Utilities": ("55", (("5510", "Utilities"),)),
    "Real Estate": ("60", (("6010", "Equity Real Estate Investment Trusts (REITs)"),)),
}

# Fix sector economics: (P/E, P/B, gross margin, EBIT margin, R&D share, capex share, leverage).
SECTOR_ECONOMICS: Dict[str, Tuple[float, float, float, float, float, float, float]] = {
    "Energy": (11.0, 1.6, 0.30, 0.12, 0.00, 0.09, 1.1),
    "Materials": (14.0, 2.0, 0.28, 0.13, 0.01, 0.06, 1.2),
    "Industrials": (18.0, 3.2, 0.30, 0.12, 0.02, 0.04, 1.6),
    "Consumer Discretionary": (19.0, 4.0, 0.36, 0.09, 0.01, 0.04, 1.7),
    "Consumer Staples": (20.0, 4.5, 0.40, 0.14, 0.01, 0.03, 1.5),
    "Health Care": (21.0, 4.2, 0.62, 0.16, 0.13, 0.03, 1.3),
    "Financials": (11.0, 1.2, np.nan, 0.30, 0.00, 0.00, 9.5),
    "Information Technology": (25.0, 7.0, 0.58, 0.24, 0.14, 0.04, 1.0),
    "Communication Services": (18.0, 3.0, 0.55, 0.20, 0.06, 0.08, 1.4),
    "Utilities": (17.0, 1.8, 0.45, 0.20, 0.00, 0.12, 2.6),
    "Real Estate": (30.0, 1.9, 0.65, 0.35, 0.00, 0.05, 1.4),
}

# Fix per-market currency mixes of the constituents: (reporting, trading, units per USD).
MARKET_CURRENCIES: Dict[str, Tuple[Tuple[str, str, float], ...]] = {
    "SP500": (("USD", "USD", 1.0),),
    "RUSSELL2000": (("USD", "USD", 1.0),),
    "STOXX600": (("EUR", "EUR", 0.90), ("GBP", "GBP", 0.78), ("CHF", "CHF", 0.92)),
    "FTSE_APAC_EX_JP": (
        ("HKD", "HKD", 7.80),
        ("AUD", "AUD", 1.45),
        ("KRW", "KRW", 1250.0),
        ("TWD", "TWD", 30.0),
        ("USD", "HKD", 1.0),
    ),
    "CSI300": (("CNY", "CNY", 6.80),),
}

# Fix the country of each currency (listing and incorporation default).
CURRENCY_COUNTRY: Dict[str, str] = {
    "USD": "US",
    "EUR": "DE",
    "GBP": "GB",
    "CHF": "CH",
    "HKD": "HK",
    "AUD": "AU",
    "KRW": "KR",
    "TWD": "TW",
    "CNY": "CN",
}

# Fix fictional name stems; no real company is represented.
NAME_STEMS: Tuple[str, ...] = (
    "Northwind",
    "Bluecrest",
    "Halvorsen",
    "Meridian",
    "Copperleaf",
    "Tidewater",
    "Arclight",
    "Stonebridge",
    "Larkspur",
    "Orinoco",
    "Veridian",
    "Kestrel",
    "Ironvale",
    "Silverline",
    "Ashgrove",
    "Brightwater",
    "Cobalt Ridge",
    "Driftwood",
    "Evergreen",
    "Foxhollow",
    "Granite Peak",
    "Harborview",
    "Juniper",
    "Keystone",
    "Lakeshore",
    "Marigold",
    "Nightingale",
    "Oakmont",
    "Pinecrest",
    "Quarry Hill",
    "Redwood",
    "Saffron",
    "Thornbury",
    "Upland",
    "Valemont",
    "Westbrook",
    "Yellowfield",
    "Zephyr",
    "Alderney",
    "Birchwood",
    "Calloway",
    "Dunmore",
    "Elmstead",
    "Fairhaven",
    "Glenmoor",
    "Hartwell",
    "Inverness",
    "Jasper Bay",
    "Kingsbury",
    "Lindqvist",
    "Morrow",
    "Newhaven",
    "Ostrander",
    "Pemberton",
    "Quintana",
)

# Map each sector to the corporate suffix that reads naturally in its names.
SECTOR_WORDS: Dict[str, str] = {
    "Energy": "Energy",
    "Materials": "Materials",
    "Industrials": "Industries",
    "Consumer Discretionary": "Brands",
    "Consumer Staples": "Foods",
    "Health Care": "Therapeutics",
    "Financials": "Financial",
    "Information Technology": "Systems",
    "Communication Services": "Media",
    "Utilities": "Power",
    "Real Estate": "Properties",
}

# Fix the scripted index turning points: (date, level) anchors per market.
INDEX_ANCHORS: Dict[str, Tuple[Tuple[str, float], ...]] = {
    "SP500": (
        ("2009-01-02", 931.0),
        ("2009-03-09", 677.0),
        ("2011-04-29", 1364.0),
        ("2011-10-03", 1099.0),
        ("2015-05-21", 2131.0),
        ("2016-02-11", 1829.0),
        ("2018-09-20", 2930.0),
        ("2018-12-24", 2351.0),
        ("2020-02-19", 3386.0),
        ("2020-03-23", 2237.0),
        ("2022-01-03", 4797.0),
        ("2022-10-12", 3577.0),
        ("2024-03-28", 5254.0),
    ),
    "RUSSELL2000": (
        ("2009-01-02", 505.0),
        ("2009-03-09", 343.0),
        ("2011-04-29", 865.0),
        ("2011-10-03", 609.0),
        ("2015-06-23", 1295.0),
        ("2016-02-11", 953.0),
        ("2018-08-31", 1740.0),
        ("2018-12-24", 1267.0),
        ("2020-01-16", 1705.0),
        ("2020-03-18", 991.0),
        ("2021-11-08", 2442.0),
        ("2022-06-16", 1649.0),
        ("2024-03-28", 2124.0),
    ),
    "STOXX600": (
        ("2009-01-02", 205.0),
        ("2009-03-09", 159.0),
        ("2011-02-17", 291.0),
        ("2011-09-22", 214.0),
        ("2015-04-15", 414.0),
        ("2016-02-11", 308.0),
        ("2018-05-22", 396.0),
        ("2018-12-27", 333.0),
        ("2020-02-19", 433.0),
        ("2020-03-18", 280.0),
        ("2022-01-05", 495.0),
        ("2022-09-29", 388.0),
        ("2024-03-28", 512.0),
    ),
    "FTSE_APAC_EX_JP": (
        ("2009-01-02", 330.0),
        ("2009-03-09", 250.0),
        ("2011-04-29", 505.0),
        ("2011-10-04", 365.0),
        ("2015-04-27", 560.0),
        ("2016-01-21", 400.0),
        ("2018-01-26", 645.0),
        ("2018-10-29", 500.0),
        ("2020-01-17", 610.0),
        ("2020-03-23", 440.0),
        ("2021-02-17", 785.0),
        ("2022-10-24", 480.0),
        ("2024-03-28", 600.0),
    ),
    "CSI300": (
        ("2009-01-05", 1880.0),
        ("2009-08-04", 3800.0),
        ("2010-07-05", 2600.0),
        ("2013-06-25", 2100.0),
        ("2015-06-08", 5380.0),
        ("2016-01-28", 2850.0),
        ("2018-01-24", 4400.0),
        ("2019-01-03", 2960.0),
        ("2021-02-10", 5800.0),
        ("2022-10-31", 3500.0),
        ("2024-02-05", 3150.0),
        ("2024-03-28", 3540.0),
    ),
}
```

#### **Step 1.2: Security identifiers with valid check digits**

ISINs use the Luhn algorithm over the letter-expanded body; CUSIPs and SEDOLs use their own weighted modulus-10 schemes.

```python
def _luhn_digit(digits: str) -> int:
    """
    Compute the Luhn check digit of a digit string (ISIN rule).

    Purpose:
        ISIN check digits apply the Luhn algorithm to the string obtained by
        expanding letters to two-digit numbers (A=10, ..., Z=35).

    Inputs:
        digits (str): The expanded, purely numeric body.

    Processes:
        Doubles every second digit from the right, sums the digit sums and
        takes the complement modulo ten.

    Outputs:
        int: The check digit in 0..9.

    Raises:
        ValueError: If the body is empty or not numeric.
    """
    # Refuse an empty or non-numeric body.
    if not digits or not digits.isdigit():
        # Name the malformed body.
        raise ValueError(f"the Luhn body must be a non-empty digit string; got {digits!r}.")
    # Accumulate the Luhn sum from the rightmost digit.
    total = 0
    # Walk the digits from the right with their positions.
    for position, char in enumerate(reversed(digits)):
        # Read the digit's value.
        value = int(char)
        # Double every digit in an even position counted from the right (0-based).
        if position % 2 == 0:
            # Double the digit.
            value *= 2
            # Fold a two-digit product into its digit sum.
            value = value - 9 if value > 9 else value
        # Add the digit's contribution.
        total += value
    # Return the complement of the sum modulo ten.
    return (10 - total % 10) % 10
```

```python
def isin_from_body(country: str, nsin: str) -> str:
    """
    Build a valid ISO 6166 ISIN from a country code and a nine-character NSIN.

    Purpose:
        Produces cross-vendor identifiers whose check digits validate.

    Inputs:
        country (str): ISO 3166 alpha-2 country code.
        nsin (str): Nine-character national security identifier.

    Processes:
        Expands letters to numbers and appends the Luhn check digit.

    Outputs:
        str: The twelve-character ISIN.

    Raises:
        ValueError: If the country is not two letters or the NSIN is not nine characters.
    """
    # Refuse a malformed country code.
    if len(country) != 2 or not country.isalpha():
        # Name the malformed code.
        raise ValueError(f"country must be two letters; got {country!r}.")
    # Refuse a malformed NSIN.
    if len(nsin) != 9 or not nsin.isalnum():
        # Name the malformed NSIN.
        raise ValueError(f"nsin must be nine alphanumeric characters; got {nsin!r}.")
    # Compose the eleven-character body.
    body = (country + nsin).upper()
    # Expand letters to two-digit numbers (A=10 ... Z=35).
    expanded = "".join(str(int(char, 36)) for char in body)
    # Append the Luhn check digit.
    return body + str(_luhn_digit(expanded))
```

```python
def cusip_from_body(body: str) -> str:
    """
    Build a valid nine-character CUSIP (or CINS) from an eight-character body.

    Purpose:
        Produces identifiers whose leading zeros and check digit are meaningful.

    Inputs:
        body (str): Eight alphanumeric characters.

    Processes:
        Applies the CUSIP modulus-10 double-add-double algorithm.

    Outputs:
        str: The nine-character identifier.

    Raises:
        ValueError: If the body is not eight alphanumeric characters.
    """
    # Refuse a malformed body.
    if len(body) != 8 or not body.isalnum():
        # Name the malformed body.
        raise ValueError(f"the CUSIP body must be eight alphanumeric characters; got {body!r}.")
    # Accumulate the CUSIP sum.
    total = 0
    # Walk the body with 1-based positions.
    for position, char in enumerate(body.upper(), start=1):
        # Map digits to themselves and letters to 10..35.
        value = int(char) if char.isdigit() else ord(char) - 55
        # Double the value in even positions.
        if position % 2 == 0:
            # Double it.
            value *= 2
        # Add the two decimal digits of the value.
        total += value // 10 + value % 10
    # Append the complement of the sum modulo ten.
    return body.upper() + str((10 - total % 10) % 10)
```

```python
def sedol_from_body(body: str) -> str:
    """
    Build a valid seven-character SEDOL from a six-character body.

    Purpose:
        Produces the identifier indispensable for the EU and APAC universes.

    Inputs:
        body (str): Six characters from digits and consonants.

    Processes:
        Applies the weighted (1, 3, 1, 7, 3, 9) modulus-10 rule.

    Outputs:
        str: The seven-character SEDOL.

    Raises:
        ValueError: If the body is not six characters or contains a vowel.
    """
    # Refuse a malformed body.
    if len(body) != 6 or not body.isalnum() or any(char in "AEIOU" for char in body.upper()):
        # Name the malformed body.
        raise ValueError(f"the SEDOL body must be six consonant/digit characters; got {body!r}.")
    # Declare the published SEDOL weights.
    weights = (1, 3, 1, 7, 3, 9)
    # Compute the weighted sum of the character values.
    total = sum(
        w * (int(c) if c.isdigit() else ord(c) - 55) for w, c in zip(weights, body.upper())
    )
    # Append the complement of the weighted sum modulo ten.
    return body.upper() + str((10 - total % 10) % 10)
```

#### **Step 1.3: The firm registry**

```python
def build_firm_registry(rng: np.random.Generator) -> pd.DataFrame:
    """
    Build the static attributes of every synthetic constituent in the five universes.

    Purpose:
        Fixes the identity, sector, currency, fiscal-year and membership facts
        each firm-quarter row inherits, so the panel is coherent across fields.

    Inputs:
        rng (np.random.Generator): The seeded PCG64 generator.

    Processes:
        1. Draws FIRMS_PER_MARKET initial constituents per market (FIRMS_PER_SECTOR
           in each of the market's four sectors) plus one replacement that enters,
           in the same sector, when a constituent exits.
        2. Interleaves the four sectors, so every market spans financial and
           non-financial business models and every sector cell stays dense.
        3. Builds ISIN, CUSIP/CINS and SEDOL identifiers with valid check digits.
        4. Records one delisting, acquisition or market-cap removal per market,
           one GICS reclassification (Information Technology to Communication
           Services, effective 2018-09-28), one fiscal-year change and two
           June fiscal-year-end filers.

    Outputs:
        pd.DataFrame: One row per issuer with its static attributes.

    Raises:
        RuntimeError: If the fictional name pool is exhausted.
    """
    # Collect one record per issuer.
    records: List[Dict[str, Any]] = []
    # Compose a pool of unique fictional names: stems crossed with qualifiers.
    qualifiers = ("", "Pacific", "Continental", "United", "Atlantic")
    # Draw the pool in a seeded random order.
    pool = [f"{stem} {q}".strip() for q in qualifiers for stem in NAME_STEMS]
    # Shuffle the pool so names never cluster by qualifier.
    stems = list(rng.permutation(pool))
    # Track the global firm counter for identifiers.
    counter = 0
    # Walk the markets in the configuration's order.
    for market_index, (market, meta) in enumerate(MARKETS.items()):
        # Read the market's four sectors.
        sectors = MARKET_SECTORS[market]
        # Build the initial constituents and one replacement firm.
        for firm_index in range(FIRMS_PER_MARKET + 1):
            # Refuse to continue when the name pool is exhausted.
            if not stems:
                # Name the exhausted pool.
                raise RuntimeError("the fictional name pool is exhausted.")
            # Take the next fictional name stem.
            stem = stems.pop()
            # Fix whether the firm is the market's replacement entrant.
            replacement = firm_index == FIRMS_PER_MARKET
            # Interleave the sectors; the replacement takes the departing firm's (firm 3) sector.
            sector = sectors[3 % 4] if replacement else sectors[firm_index % 4]
            # Read the sector's code and industry groups.
            sector_code, groups = GICS[sector]
            # Choose the industry group of the firm (alternating within the sector).
            group_code, group_name = groups[(firm_index // 4) % len(groups)]
            # Choose the firm's reporting and trading currencies.
            reporting, trading, units = MARKET_CURRENCIES[market][
                firm_index % len(MARKET_CURRENCIES[market])
            ]
            # Resolve the listing country from the trading currency.
            listing_country = CURRENCY_COUNTRY[trading]
            # Resolve incorporation (the cross-listed USD reporter is a Cayman Islands company).
            incorporation = (
                "KY" if (reporting, trading) == ("USD", "HKD") else CURRENCY_COUNTRY[reporting]
            )
            # Compose a unique fictional ticker: two stem letters and a two-letter serial.
            ticker = (
                stem.replace(" ", "").upper()[:2]
                + chr(65 + counter // 26 % 26)
                + chr(65 + counter % 26)
            )
            # Compose the vendor canonical key.
            issuer_id = f"{ticker} {meta['suffix']} Equity"
            # Compose an eight-character CUSIP/CINS body (CINS uses a country letter prefix).
            prefix = (
                ""
                if listing_country == "US"
                else {
                    "DE": "D",
                    "GB": "G",
                    "CH": "H",
                    "HK": "Y",
                    "AU": "Q",
                    "KR": "Y",
                    "TW": "Y",
                    "CN": "Y",
                }[listing_country]
            )
            # Pad the numeric part so leading zeros are meaningful.
            cusip_body = prefix + f"{counter * 7919 % 10 ** (8 - len(prefix)):0{8 - len(prefix)}d}"
            # Compose a SEDOL body from consonants and digits.
            sedol_body = "B" + f"{counter * 104729 % 100000:05d}"
            # Compose the national identifier inside the ISIN.
            nsin = (
                cusip_body + "0"
                if listing_country == "US"
                else f"{counter * 15485863 % 10 ** 9:09d}"
            )
            # Assign the entry date: initial constituents entered before the panel.
            entry = (
                pd.Timestamp("2016-07-01")
                if replacement
                else pd.Timestamp("2004-01-02") + pd.Timedelta(days=int(rng.integers(0, 2500)))
            )
            # Assign the exit of the market's departing constituent (firm 3).
            exit_date = pd.Timestamp("2016-06-17") if firm_index == 3 else pd.NaT
            # Cycle the exit reasons across markets so the extract is not survivorship-free.
            exit_reason = (
                ("DELISTED", "ACQUIRED", "REMOVED_MARKETCAP", "ACQUIRED", "DELISTED")[market_index]
                if firm_index == 3
                else None
            )
            # Fix a June fiscal year-end for firm 2 of APAC and S&P 500 (vendor style only).
            june_fye = (
                FISCAL_LABEL_STYLE == "vendor"
                and firm_index == 1
                and market in ("FTSE_APAC_EX_JP", "SP500")
            )
            # Record the static attributes.
            records.append(
                {
                    "market": market,
                    "issuer_id": issuer_id,
                    "ticker": ticker,
                    "company_name": (
                        f"{stem} {SECTOR_WORDS[sector]} "
                        f"{'Inc.' if market == 'SP500' else 'Holdings Ltd'}"
                    ),
                    "isin": isin_from_body(listing_country, nsin),
                    "cusip": cusip_from_body(cusip_body),
                    "sedol": sedol_from_body(sedol_body),
                    "reporting_currency": reporting,
                    "trading_currency": trading,
                    "units_per_usd": units,
                    "country_of_incorporation": incorporation,
                    "country_of_listing": listing_country,
                    "gics_sector_name": sector,
                    "gics_sector_code": sector_code,
                    "gics_industry_group_code": group_code,
                    "gics_industry_group_name": group_name,
                    "entry_date": entry,
                    "exit_date": exit_date,
                    "exit_reason": exit_reason,
                    "june_fiscal_year_end": june_fye,
                    "fiscal_year_change": FISCAL_LABEL_STYLE == "vendor"
                    and firm_index == 2
                    and market == "RUSSELL2000",
                    "loss_making": firm_index == 5 and market == "RUSSELL2000",
                    "reclassified_2018": sector == "Information Technology" and firm_index < 4,
                    "size": float(np.exp(rng.normal(0.0, 0.6)))
                    * (0.12 if market == "RUSSELL2000" else 1.0),
                }
            )
            # Advance the identifier counter.
            counter += 1
    # Return the registry.
    return pd.DataFrame(records)
```

#### **Step 1.4: `index_daily` (L3)**

```python
def generate_index_daily(rng: np.random.Generator) -> pd.DataFrame:
    """
    Generate the L3 raw index price series (Yahoo Finance schema) for the five universes.

    Purpose:
        Supplies the daily closes from which Task 6 dates bull and bear states:
        "a bull market is declared when the index has risen at least 20% from
        its most recent trough, and a bear market when it has fallen at least
        20% from its most recent peak."

    Inputs:
        rng (np.random.Generator): The seeded PCG64 generator.

    Processes:
        1. Builds business-day calendars from 2009-01-02 to the extract date.
        2. Interpolates log levels through scripted turning points that span
           genuine >= 20% rises and falls, then adds a Brownian bridge between
           consecutive anchors (daily volatility 0.9%), so every anchor is hit
           exactly and the path is rough in between.
        3. Derives open/high/low around the close, adj_close as a backward-
           adjusted series (which regime dating must NOT use) and volume.

    Outputs:
        pd.DataFrame: Columns index_ticker, market_id, ticker_verified,
        trading_date, open, high, low, close, adj_close, volume, currency,
        trading_calendar_id.

    Raises:
        ValueError: If an anchor list is not strictly increasing in time.
    """
    # Collect one frame per index.
    frames: List[pd.DataFrame] = []
    # Walk the markets with their index metadata.
    for market, meta in MARKETS.items():
        # Read the anchors as timestamps and log levels.
        anchors = [
            (pd.Timestamp(day), float(np.log(level))) for day, level in INDEX_ANCHORS[market]
        ]
        # Refuse anchors that are not strictly increasing in time.
        if any(b[0] <= a[0] for a, b in zip(anchors, anchors[1:])):
            # Name the market with malformed anchors.
            raise ValueError(f"the index anchors of {market} must be strictly increasing in time.")
        # List the business days spanned by the anchors.
        days = pd.bdate_range(anchors[0][0], EXTRACT_DATE)
        # Collect the log path segment by segment.
        log_path = np.empty(len(days))
        # Walk consecutive anchor pairs.
        for (start, level0), (end, level1) in zip(
            anchors, anchors[1:] + [(EXTRACT_DATE, anchors[-1][1])]
        ):
            # Select the days of the segment, inclusive of its start.
            mask = (days >= start) & (days <= end)
            # Count the segment's days.
            n = int(mask.sum())
            # Skip an empty segment.
            if n == 0:
                # Move to the next pair.
                continue
            # Draw the Brownian increments of the segment (daily vol 0.9%).
            walk = np.cumsum(rng.normal(0.0, 0.009, n))
            # Pin the bridge to zero at both ends: B_t = W_t - (t/n) W_n.
            bridge = walk - np.linspace(0.0, 1.0, n) * walk[-1]
            # Interpolate the log level linearly between the anchors and add the bridge.
            log_path[mask] = np.linspace(level0, level1, n) + bridge
        # Convert the log path to closes.
        close = np.exp(log_path)
        # Draw the intraday range as a fraction of the close.
        spread = np.abs(rng.normal(0.0, 0.006, len(days)))
        # Set the open at the previous close plus a small gap.
        open_ = np.r_[close[0], close[:-1]] * np.exp(rng.normal(0.0, 0.002, len(days)))
        # Bound the high above both open and close.
        high = np.maximum(open_, close) * (1.0 + spread)
        # Bound the low below both open and close.
        low = np.minimum(open_, close) * (1.0 - spread)
        # Backward-adjust the close for a 1.8% dividend yield (adj_close: never used for regimes).
        years_to_end = (EXTRACT_DATE - days).days / 365.25
        # Apply the backward adjustment factor.
        adj_close = close * np.exp(-0.018 * years_to_end)
        # Assemble the index frame.
        frames.append(
            pd.DataFrame(
                {
                    "index_ticker": meta["ticker"],
                    "market_id": market,
                    "ticker_verified": True,
                    "trading_date": days,
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": close,
                    "adj_close": adj_close,
                    "volume": rng.lognormal(20.0, 0.3, len(days)).round(0),
                    "currency": meta["currency"],
                    "trading_calendar_id": meta["calendar"],
                }
            )
        )
    # Stack the five indices.
    index_daily = pd.concat(frames, ignore_index=True)
    # The FTSE leg's symbol is unverified at extraction; Task 3 resolves and verifies it.
    index_daily.loc[index_daily["market_id"] == "FTSE_APAC_EX_JP", "ticker_verified"] = False
    # Return the panel typed as the L3 schema declares.
    return index_daily.astype(
        {"trading_date": "datetime64[ns]", "volume": "float64", "ticker_verified": "bool"}
    )
```

#### **Step 1.5: The quarterly calendar and fiscal labels**

```python
def _quarter_ends(first: str, last: str) -> List[pd.Timestamp]:
    """
    List calendar quarter-end dates between two quarter labels, inclusive.

    Purpose:
        Supplies the period-end grid of the panel.

    Inputs:
        first (str): First quarter label, e.g. "2011Q1".
        last (str): Last quarter label, e.g. "2023Q4".

    Processes:
        Builds a quarterly PeriodIndex and takes each period's last day.

    Outputs:
        List[pd.Timestamp]: The quarter-end dates.

    Raises:
        ValueError: If first is after last.
    """
    # Build the quarterly periods.
    periods = pd.period_range(first, last, freq="Q")
    # Refuse an empty range.
    if len(periods) == 0:
        # Name the malformed range.
        raise ValueError(f"the quarter range {first}..{last} is empty.")
    # Return the normalised quarter-end dates.
    return [period.end_time.normalize() for period in periods]
```

```python
def _fiscal_label(period_end: pd.Timestamp, june_fye: bool) -> Tuple[str, int, int]:
    """
    Compute a firm's fiscal label, year and quarter for a period end.

    Purpose:
        Implements idiosyncratic fiscal numbering, on which all lag construction
        is based (Task 10 parses year * 4 + quarter - 1 from this label).

    Inputs:
        period_end (pd.Timestamp): The fiscal quarter's end.
        june_fye (bool): Whether the fiscal year ends in June.

    Processes:
        Calendar filers number quarters by calendar quarter; June filers start
        fiscal Q1 in July and name the fiscal year by its June end.

    Outputs:
        Tuple[str, int, int]: (label "FY2019Q3", fiscal year, fiscal quarter).

    Raises:
        ValueError: If the date is not a quarter end.
    """
    # Refuse a date that is not a calendar quarter end.
    if period_end.month not in (3, 6, 9, 12):
        # Name the malformed date.
        raise ValueError(f"{period_end.date()} is not a calendar quarter end.")
    # Number the calendar quarter of the date.
    calendar_quarter = (period_end.month - 1) // 3 + 1
    # Shift the numbering for a June fiscal year end.
    if june_fye:
        # Fiscal Q1 is July-September; the fiscal year is named by its June end.
        quarter = (calendar_quarter + 1) % 4 + 1
        # Name the fiscal year by the June in which it ends.
        year = period_end.year + (1 if period_end.month > 6 else 0)
    else:
        # Calendar filers keep calendar numbering.
        quarter, year = calendar_quarter, period_end.year
    # Return the label in the declared style, with the fiscal year and quarter.
    return (
        (f"{year}Q{quarter}" if FISCAL_LABEL_STYLE == "calendar" else f"FY{year}Q{quarter}"),
        year,
        quarter,
    )
```

#### **Step 1.6: `fundamental_quarter` (L1)**

```python
def generate_fundamental_quarter(
    firms: pd.DataFrame, index_daily: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    """
    Generate the L1 raw firm-quarter fundamental extraction (Bloomberg schema).

    Purpose:
        Produces the primary feature source of the disentangled discovery
        machinery: point-in-time, as-originally-filed quarterly fundamentals of
        every constituent-quarter, with the look-ahead gate, the TTM aggregates,
        the balance-sheet identity, the forward-shifted target and the five
        operational columns config.yaml declares (market, target_date, target,
        bs_shares_diluted, enterprise_value).

    Inputs:
        firms (pd.DataFrame): The registry from build_firm_registry.
        index_daily (pd.DataFrame): The L3 panel (market sentiment factor).
        rng (np.random.Generator): The seeded PCG64 generator.

    Processes:
        1. Simulates quarterly revenue with drift, seasonality and shocks from
           2011Q1 (TTM warm-up) to 2023Q4, restricted to each firm's membership.
        2. Derives the income statement from sector margins: EBIT, EBITDA =
           EBIT + D&A, NI = (EBIT - interest expense + interest income)(1 - tax).
        3. Forms TTM aggregates as four-quarter sums (no double counting) and
           EPS_TTM = NI_TTM / time-weighted shares.
        4. Rolls equity forward by retained earnings and sets total assets =
           liabilities + equity exactly (Gate 0's accounting identity).
        5. Prices each firm as Metric x Multiple (EPS x sector P/E, or BVPS x
           sector P/B for loss-makers) scaled by the index's deviation from trend
           and idiosyncratic noise, converts to the trading currency, and sets
           market cap = price x period-end shares exactly.
        6. Forward-shifts the next quarter's close into target and records
           target_date as the next fiscal period end.
        7. Sets structural zeros (banks: R&D, capex, current assets; insurers,
           utilities, REITs: R&D) and structural absences (banks: cost of
           revenue, gross profit), restatement flags and missing-field counts.

    Outputs:
        pd.DataFrame: The 79 columns of validation.fundamental_schema.columns,
        typed exactly as validation.fundamental_schema.dtypes.

    Raises:
        ValueError: If the registry lacks a required attribute.
    """
    # Name the registry attributes the generator reads.
    required = {"market", "issuer_id", "gics_sector_name", "entry_date", "exit_date", "size"}
    # Refuse a registry that lacks them.
    if not required.issubset(firms.columns):
        # Name the missing attributes.
        raise ValueError(f"the firm registry lacks {sorted(required - set(firms.columns))}.")
    # Compute each market's quarter-end index level relative to its log-linear trend.
    sentiment: Dict[str, pd.Series] = {}
    # Walk the markets of the index panel.
    for market, rows in index_daily.groupby("market_id"):
        # Take the last close of each calendar quarter.
        quarterly = rows.set_index("trading_date")["close"].resample("QE").last()
        # Fit the log-linear trend of the quarterly closes.
        t = np.arange(len(quarterly))
        # Estimate the trend coefficients by least squares.
        slope, intercept = np.polyfit(t, np.log(quarterly.to_numpy()), 1)
        # Store exp(log close - trend), the market sentiment multiplier.
        sentiment[market] = pd.Series(
            np.exp(np.log(quarterly.to_numpy()) - (intercept + slope * t)),
            index=quarterly.index.normalize(),
        )
    # List the quarter ends including the 2011 warm-up year.
    quarter_ends = _quarter_ends("2011Q1", PANEL_LAST_QUARTER)
    # Fix the first quarter end that is published.
    first_published = pd.Period(PANEL_FIRST_QUARTER, freq="Q").end_time.normalize()
    # Collect the published rows.
    rows_out: List[Dict[str, Any]] = []
    # Walk the firms.
    for firm in firms.itertuples(index=False):
        # Read the sector economics.
        pe, pb, gross_margin, ebit_margin, rd_share, capex_share, leverage = SECTOR_ECONOMICS[
            firm.gics_sector_name
        ]
        # Fix whether the firm is a bank, an insurer or a structural-zero R&D industry.
        is_bank = firm.gics_industry_group_code == "4010"
        # Fix the industry groups with structural zero R&D (banks, insurers, utilities, REITs).
        rd_zero = firm.gics_industry_group_code in ("4010", "4030", "5510", "6010")
        # Scale every monetary value by the reporting currency's units per USD.
        units = firm.units_per_usd
        # Draw the base quarterly revenue in millions of reporting currency.
        revenue_q = 1500.0 * firm.size * units
        # Draw the period-end share count in millions.
        shares = float(rng.uniform(150.0, 1500.0)) * (
            0.15 if firm.market == "RUSSELL2000" else 1.0
        )
        # Initialise equity from the sector P/B identity at the start.
        equity = revenue_q * 4.0 * ebit_margin * 0.75 * pe / pb
        # Draw the firm's quarterly revenue drift.
        drift = float(rng.normal(0.012, 0.008))
        # Draw the firm's payout ratio (non-payers have zero).
        payout = 0.0 if firm.loss_making or rng.random() < 0.25 else float(rng.uniform(0.2, 0.6))
        # Set the corporate tax rate by listing country.
        tax_rate = 0.21 if firm.country_of_listing == "US" else 0.25
        # Hold the firm's quarterly history for the TTM windows.
        history: List[Dict[str, float]] = []
        # Walk the quarter ends.
        for position, period_end in enumerate(quarter_ends):
            # Skip quarters before entry or after exit; rows exist only for constituent quarters.
            if period_end < firm.entry_date - pd.Timedelta(days=365) or (
                not pd.isna(firm.exit_date) and period_end > firm.exit_date
            ):
                # Move to the next quarter.
                continue
            # Grow revenue with drift, seasonality and a cyclical shock.
            revenue_q *= float(
                np.exp(drift + 0.02 * np.sin(position * np.pi / 2) + rng.normal(0.0, 0.03))
            )
            # Read the market sentiment multiplier at this quarter end.
            mood = float(sentiment[firm.market].get(period_end, 1.0))
            # Derive EBIT from the sector margin, moving with the cycle.
            ebit_q = revenue_q * ebit_margin * (0.85 + 0.3 * mood) * float(rng.normal(1.0, 0.05))
            # Turn the loss-making biotech's EBIT negative.
            if firm.loss_making:
                # Burn cash: operating loss of 40% of revenue.
                ebit_q = -0.40 * revenue_q
            # Derive depreciation and amortisation from revenue.
            da_q = revenue_q * 0.04
            # Set liabilities from the sector leverage on equity.
            liabilities = equity * leverage
            # Set interest-bearing debt as a share of liabilities.
            debt = liabilities * (0.15 if is_bank else 0.55)
            # Set cash and equivalents as a share of total assets.
            cash = (equity + liabilities) * (0.06 if is_bank else 0.10)
            # Compute quarterly interest expense on debt at 4% a year.
            interest_expense = debt * 0.04 / 4.0
            # Compute quarterly interest income on cash at 2% a year.
            interest_income = cash * 0.02 / 4.0
            # Compute pre-tax income.
            pretax = ebit_q - interest_expense + interest_income
            # Compute the income tax expense (negative is a credit).
            tax = pretax * tax_rate
            # Compute quarterly net income.
            net_income_q = pretax - tax
            # Compute quarterly dividends from the payout ratio on positive income.
            dividends_q = payout * max(net_income_q, 0.0)
            # Roll equity forward by retained earnings.
            equity = equity + net_income_q - dividends_q
            # Adjust shares by a slow buyback or issuance.
            shares *= float(np.exp(rng.normal(-0.002, 0.004)))
            # Record the quarter's flows.
            history.append(
                {
                    "revenue": revenue_q,
                    "ebit": ebit_q,
                    "da": da_q,
                    "ni": net_income_q,
                    "rd": 0.0 if rd_zero else revenue_q * rd_share,
                    "dividends": dividends_q,
                    "capex": 0.0 if is_bank else revenue_q * capex_share,
                    "shares": shares,
                    "ocf": net_income_q + da_q + revenue_q * float(rng.normal(0.0, 0.02)),
                }
            )
            # Publish nothing before the panel start or with fewer than four quarters of history.
            if period_end < first_published or len(history) < 4:
                # Move to the next quarter.
                continue
            # Take the trailing four quarters.
            window = history[-4:]
            # Sum each flow over the trailing twelve months.
            ttm = {key: float(sum(q[key] for q in window)) for key in window[0]}
            # Compute the time-weighted average shares of the window.
            weighted_shares = float(np.mean([q["shares"] for q in window]))
            # Compute total assets by the accounting identity A = L + E.
            total_assets = liabilities + equity
            # Compute goodwill and intangibles as a share of assets.
            goodwill_intangibles = total_assets * (0.02 if is_bank else 0.18)
            # Compute TTM free cash flow (may be negative; never truncated).
            fcf_ttm = ttm["ocf"] - ttm["capex"]
            # Compute EPS_TTM on time-weighted shares.
            eps_ttm = ttm["ni"] / weighted_shares
            # Compute book value per share.
            bvps = equity / shares
            # Price as Metric x Multiple: EPS x sector P/E, or BVPS x P/B for loss-makers.
            anchor = eps_ttm * pe if eps_ttm > 0 else bvps * pb
            # Scale by market sentiment and idiosyncratic noise (reporting currency).
            price_reporting = anchor * mood * float(np.exp(rng.normal(0.0, 0.08)))
            # Resolve the reporting-to-trading FX rate (identity for matched currencies).
            fx = (
                7.80 if (firm.reporting_currency, firm.trading_currency) == ("USD", "HKD") else 1.0
            )
            # Convert the price to the trading currency.
            price = max(price_reporting * fx, 0.01)
            # Compute market capitalisation on period-end shares (trading currency, millions).
            market_cap = price * shares
            # Label the fiscal period.
            label, fiscal_year, fiscal_quarter = _fiscal_label(
                period_end, bool(firm.june_fiscal_year_end)
            )
            # Detect the fiscal-year change of the designated firm (December to June in 2017).
            change_row = bool(firm.fiscal_year_change) and period_end == pd.Timestamp("2017-03-31")
            # Relabel quarters after the change with June fiscal numbering.
            if firm.fiscal_year_change and period_end >= pd.Timestamp("2017-03-31"):
                # Apply the June fiscal year from the change onwards.
                label, fiscal_year, fiscal_quarter = _fiscal_label(period_end, True)
            # Fix the original filing lag (annual reports take longer).
            lag_days = (
                int(rng.integers(55, 75)) if fiscal_quarter == 4 else int(rng.integers(25, 45))
            )
            # Date the original filing.
            filing_original = period_end + pd.Timedelta(days=lag_days)
            # Flag a vendor value that differs from the as-filed snapshot (about 1% of rows).
            restated = rng.random() < 0.01
            # Assemble the row.
            rows_out.append(
                {
                    "market": firm.market,
                    "issuer_id": firm.issuer_id,
                    "isin": firm.isin,
                    "cusip": firm.cusip,
                    "sedol": firm.sedol,
                    "ticker": firm.ticker,
                    "company_name": firm.company_name,
                    "reporting_currency": firm.reporting_currency,
                    "trading_currency": firm.trading_currency,
                    "fx_reporting_to_trading_rate": fx,
                    "country_of_incorporation": firm.country_of_incorporation,
                    "country_of_listing": firm.country_of_listing,
                    "gics_sector_code": (
                        "50"
                        if firm.reclassified_2018 and period_end >= pd.Timestamp("2018-09-28")
                        else firm.gics_sector_code
                    ),
                    "gics_sector_name": (
                        "Communication Services"
                        if firm.reclassified_2018 and period_end >= pd.Timestamp("2018-09-28")
                        else firm.gics_sector_name
                    ),
                    "gics_industry_group_code": (
                        "5020"
                        if firm.reclassified_2018 and period_end >= pd.Timestamp("2018-09-28")
                        else firm.gics_industry_group_code
                    ),
                    "gics_industry_group_name": (
                        "Media & Entertainment"
                        if firm.reclassified_2018 and period_end >= pd.Timestamp("2018-09-28")
                        else firm.gics_industry_group_name
                    ),
                    "gics_classification_effective_date": (
                        pd.Timestamp("2018-09-28")
                        if firm.reclassified_2018 and period_end >= pd.Timestamp("2018-09-28")
                        else pd.Timestamp("1999-08-01")
                    ),
                    "gics_sector_code_effective": (
                        "50"
                        if firm.reclassified_2018 and period_end >= pd.Timestamp("2018-09-28")
                        else firm.gics_sector_code
                    ),
                    "fiscal_period_end": period_end,
                    "fiscal_quarter_label": label,
                    "fiscal_year": fiscal_year,
                    "fiscal_quarter_number": fiscal_quarter,
                    "filing_date_original": filing_original,
                    "filing_date_latest_restated": (
                        filing_original + pd.Timedelta(days=200) if restated else filing_original
                    ),
                    "flag_restatement_audit_diff": int(restated),
                    "filing_type": (
                        ("10-K" if fiscal_quarter == 4 else "10-Q")
                        if firm.country_of_listing == "US"
                        else ("CAS" if firm.market == "CSI300" else "IFRS")
                    ),
                    "period_type": "QUARTERLY",
                    "is_revenue_q": revenue_q,
                    "is_cost_of_revenue_q": (
                        np.nan if is_bank else revenue_q * (1.0 - gross_margin)
                    ),
                    "is_gross_profit_q": np.nan if is_bank else revenue_q * gross_margin,
                    "is_operating_income_q": ebit_q,
                    "is_ebit_q": ebit_q,
                    "is_ebitda_q": ebit_q + da_q,
                    "is_net_income_q": net_income_q,
                    "is_eps_basic_q": net_income_q / shares,
                    "is_eps_diluted_q": net_income_q / (shares * 1.015),
                    "is_interest_expense_q": interest_expense,
                    "is_interest_income_q": interest_income,
                    "is_income_tax_expense_q": tax,
                    "is_rd_expense_q": history[-1]["rd"],
                    "is_sga_q": revenue_q * 0.12,
                    "is_revenue_ttm": ttm["revenue"],
                    "is_net_income_ttm": ttm["ni"],
                    "is_eps_ttm": eps_ttm,
                    "bs_shares_outstanding_weighted_avg_ttm": weighted_shares,
                    "is_ebit_ttm": ttm["ebit"],
                    "is_ebitda_ttm": ttm["ebit"] + ttm["da"],
                    "is_rd_expense_ttm": ttm["rd"],
                    "cf_operating_cash_flow_ttm": ttm["ocf"],
                    "cf_capital_expenditure_ttm": ttm["capex"],
                    "cf_free_cash_flow_ttm": fcf_ttm,
                    "cf_dividends_paid_ttm": ttm["dividends"],
                    "cf_depreciation_amortization_ttm": ttm["da"],
                    "cf_cash_from_investing_ttm": -1.3 * ttm["capex"],
                    "cf_cash_from_financing_ttm": -ttm["dividends"]
                    + float(rng.normal(0.0, 0.02)) * ttm["revenue"],
                    "bs_total_assets": total_assets,
                    "bs_current_assets": 0.0 if is_bank else total_assets * 0.35,
                    "bs_cash_and_equivalents": cash,
                    "bs_total_liabilities": liabilities,
                    "bs_current_liabilities": 0.0 if is_bank else liabilities * 0.40,
                    "bs_total_debt": debt,
                    "bs_total_debt_convention": (
                        "IB_only"
                        if firm.country_of_listing == "US"
                        and period_end < pd.Timestamp("2019-01-01")
                        else "IB+leases"
                    ),
                    "bs_long_term_investments": total_assets * (0.30 if is_bank else 0.05),
                    "bs_goodwill_and_intangibles": goodwill_intangibles,
                    "bs_goodwill_separable": goodwill_intangibles * 0.7,
                    "bs_total_equity": equity,
                    "bs_total_equity_convention": "common",
                    "bs_shares_outstanding": shares,
                    "px_close_period_end": price,
                    "px_split_adjustment_reference_date": EXTRACT_DATE,
                    "market_cap_period_end": market_cap,
                    "market_cap_period_end_share_basis": "period_end_shares",
                    "flag_restatement_pending": bool(rng.random() < 0.005),
                    "flag_fiscal_year_change": change_row,
                    "bs_shares_diluted": shares * 1.015,
                    "enterprise_value": market_cap / fx + debt - cash,
                }
            )
    # Assemble the panel.
    panel = pd.DataFrame(rows_out).sort_values(
        ["issuer_id", "fiscal_period_end"], ignore_index=True
    )
    # Forward-shift the next fiscal quarter's close within issuer: y_{i,t+1}.
    panel["target"] = panel.groupby("issuer_id")["px_close_period_end"].shift(-1)
    # Record the target date as the next fiscal period end of the same issuer.
    panel["target_date"] = panel.groupby("issuer_id")["fiscal_period_end"].shift(-1)
    # Close the last row of each issuer one quarter ahead, where the target is unobserved.
    panel["target_date"] = panel["target_date"].fillna(
        panel["fiscal_period_end"] + pd.offsets.QuarterEnd(1)
    )
    # Inject sparse vendor gaps in non-critical fields (about 1%).
    for column in (
        "is_interest_income_q",
        "cf_depreciation_amortization_ttm",
        "bs_long_term_investments",
    ):
        # Blank the drawn cells.
        panel.loc[rng.random(len(panel)) < 0.01, column] = np.nan
    # Name the operational columns, which are not L1 vendor fields.
    operational = ["market", "target", "target_date", "bs_shares_diluted", "enterprise_value"]
    # Count the missing L1 fields per row (structural absences included, as the vendor reports).
    panel["n_missing_fields"] = panel.drop(columns=operational).isna().sum(axis=1).astype("int64")
    # Return the panel in the declared column order.
    return panel
```

#### **Step 1.7: `macro_quarter` (L2)**

```python
def generate_macro_quarter(rng: np.random.Generator) -> pd.DataFrame:
    """
    Generate the L2 raw macroeconomic extraction (FactSet schema), one row per (quarter, market).

    Purpose:
        Supplies the sovereign curves (Y_30 enters the PySR S&P 500 equation and
        the Gordon discount rate r = local yield + ERP), inflation, activity and
        credit conditions, with publication dates and initial-release vintages.

    Inputs:
        rng (np.random.Generator): The seeded PCG64 generator.

    Processes:
        1. Interpolates annual anchor levels of each curve and adds AR(1) noise.
        2. Writes every sovereign series on every row (they are global
           observables) and resolves y_30_local to the market's own 30-year
           yield (US for SP500 and RUSSELL2000, Bund for STOXX600, Gilt for
           FTSE_APAC_EX_JP as the schema states, CGB for CSI300).
        3. Derives term_spread_30_3m = y_30_local - y_3m_us and
           real_yield_10 = y_10 - cpi_yoy of the market.

    Outputs:
        pd.DataFrame: The L2 columns plus market_id (the market label config.yaml joins on).

    Raises:
        ValueError: Never for the declared anchors; reserved for malformed anchors.
    """
    # List the calendar quarters, including the 2011 warm-up and a lead quarter.
    quarters = pd.period_range("2011Q1", "2024Q1", freq="Q")
    # Fix annual anchors (percent) of each series, 2011..2024.
    anchors: Dict[str, List[float]] = {
        "y_30_us": [3.9, 2.9, 3.4, 3.1, 2.8, 2.6, 2.9, 3.0, 2.6, 1.6, 1.9, 3.2, 4.1, 4.3],
        "y_10_us": [2.8, 1.8, 2.4, 2.5, 2.1, 1.8, 2.3, 2.9, 2.1, 0.9, 1.4, 3.0, 4.0, 4.2],
        "y_5_us": [1.5, 0.8, 1.2, 1.6, 1.5, 1.3, 1.9, 2.7, 1.9, 0.5, 0.9, 3.0, 4.1, 4.2],
        "y_2_us": [0.4, 0.3, 0.3, 0.5, 0.7, 0.8, 1.4, 2.5, 1.9, 0.4, 0.3, 3.0, 4.6, 4.6],
        "y_3m_us": [0.05, 0.08, 0.05, 0.03, 0.05, 0.3, 0.9, 2.0, 2.1, 0.4, 0.05, 2.1, 5.2, 5.3],
        "y_30_de": [3.0, 2.2, 2.3, 1.7, 0.9, 0.6, 1.2, 1.0, 0.2, 0.1, 0.1, 1.6, 2.5, 2.5],
        "y_10_de": [2.6, 1.5, 1.6, 1.2, 0.5, 0.1, 0.4, 0.4, -0.2, -0.5, -0.3, 1.2, 2.4, 2.3],
        "y_30_gb": [4.0, 3.1, 3.4, 3.1, 2.6, 2.0, 1.8, 1.8, 1.3, 0.9, 1.2, 2.8, 4.4, 4.5],
        "y_10_gb": [3.0, 1.9, 2.4, 2.1, 1.8, 1.2, 1.2, 1.4, 0.9, 0.3, 0.8, 2.4, 4.0, 4.0],
        "y_30_cn": [4.4, 4.2, 4.6, 4.5, 3.9, 3.4, 4.3, 4.1, 3.8, 3.7, 3.6, 3.2, 2.9, 2.5],
        "y_10_cn": [3.8, 3.4, 3.9, 4.1, 3.3, 2.9, 3.6, 3.6, 3.2, 3.0, 3.0, 2.8, 2.7, 2.3],
        "credit_spread_ig": [1.8, 1.6, 1.3, 1.1, 1.4, 1.4, 1.0, 1.2, 1.1, 1.5, 0.9, 1.4, 1.2, 1.0],
        "credit_spread_hy": [6.0, 5.6, 4.5, 4.0, 5.5, 5.4, 3.5, 4.2, 4.0, 5.3, 3.2, 4.8, 3.9, 3.3],
        "vix_quarter_mean": [
            24.0,
            18.0,
            14.0,
            14.0,
            17.0,
            16.0,
            11.0,
            17.0,
            15.0,
            29.0,
            19.0,
            26.0,
            17.0,
            14.0,
        ],
        "fx_trade_weighted_index": [
            95.0,
            98.0,
            99.0,
            102.0,
            115.0,
            119.0,
            117.0,
            116.0,
            120.0,
            119.0,
            114.0,
            125.0,
            121.0,
            122.0,
        ],
        "commodity_index": [
            580.0,
            560.0,
            530.0,
            470.0,
            330.0,
            300.0,
            330.0,
            360.0,
            330.0,
            280.0,
            420.0,
            560.0,
            470.0,
            460.0,
        ],
    }
    # Fix per-market macro anchors (CPI YoY, PPI YoY, IP YoY, unemployment, real GDP YoY).
    domestic: Dict[str, Dict[str, List[float]]] = {
        "US": {
            "cpi_yoy": [3.1, 2.1, 1.5, 1.6, 0.1, 1.3, 2.1, 2.4, 1.8, 1.2, 4.7, 8.0, 4.1, 3.2],
            "unemployment_rate": [
                8.9,
                8.1,
                7.4,
                6.2,
                5.3,
                4.9,
                4.4,
                3.9,
                3.7,
                8.1,
                5.4,
                3.6,
                3.6,
                3.8,
            ],
            "real_gdp_growth_yoy": [
                1.6,
                2.3,
                2.1,
                2.5,
                2.9,
                1.8,
                2.5,
                3.0,
                2.5,
                -2.2,
                5.8,
                1.9,
                2.5,
                2.8,
            ],
        },
        "DE": {
            "cpi_yoy": [2.5, 2.1, 1.6, 0.8, 0.7, 0.4, 1.7, 1.9, 1.4, 0.4, 3.2, 8.7, 6.0, 2.5],
            "unemployment_rate": [
                5.8,
                5.4,
                5.2,
                5.0,
                4.6,
                4.1,
                3.8,
                3.4,
                3.1,
                3.8,
                3.6,
                3.1,
                3.0,
                3.2,
            ],
            "real_gdp_growth_yoy": [
                3.9,
                0.4,
                0.4,
                2.2,
                1.5,
                2.2,
                2.7,
                1.0,
                1.1,
                -3.8,
                3.2,
                1.8,
                -0.3,
                0.2,
            ],
        },
        "GB": {
            "cpi_yoy": [4.5, 2.8, 2.6, 1.5, 0.0, 0.7, 2.7, 2.5, 1.8, 0.9, 2.6, 9.1, 7.3, 3.2],
            "unemployment_rate": [
                8.1,
                8.0,
                7.6,
                6.2,
                5.4,
                4.9,
                4.4,
                4.1,
                3.8,
                4.6,
                4.5,
                3.7,
                4.0,
                4.2,
            ],
            "real_gdp_growth_yoy": [
                1.1,
                1.5,
                1.8,
                3.2,
                2.2,
                1.9,
                2.7,
                1.4,
                1.6,
                -10.4,
                8.7,
                4.3,
                0.1,
                0.5,
            ],
        },
        "CN": {
            "cpi_yoy": [5.4, 2.6, 2.6, 2.0, 1.4, 2.0, 1.6, 2.1, 2.9, 2.5, 0.9, 2.0, 0.2, 0.1],
            "unemployment_rate": [
                4.1,
                4.1,
                4.1,
                4.1,
                4.0,
                4.0,
                3.9,
                4.9,
                5.2,
                5.6,
                5.1,
                5.6,
                5.2,
                5.2,
            ],
            "real_gdp_growth_yoy": [
                9.6,
                7.9,
                7.8,
                7.4,
                7.0,
                6.8,
                6.9,
                6.7,
                6.0,
                2.2,
                8.4,
                3.0,
                5.2,
                5.3,
            ],
        },
    }
    # Map each market to its domestic economy, local 30-year yield and local 10-year yield.
    market_economy = {
        "SP500": ("US", "y_30_us", "y_10_us"),
        "RUSSELL2000": ("US", "y_30_us", "y_10_us"),
        "STOXX600": ("DE", "y_30_de", "y_10_de"),
        "FTSE_APAC_EX_JP": ("GB", "y_30_gb", "y_10_gb"),
        "CSI300": ("CN", "y_30_cn", "y_10_cn"),
    }

    # Interpolate a quarterly path through annual anchors with AR(1) noise.
    def path(levels: Sequence[float], scale: float) -> np.ndarray:
        """
        Interpolate quarterly values through annual anchors and add AR(1) noise.

        Inputs:
            levels (Sequence[float]): One anchor per year, 2011..2024.
            scale (float): Innovation standard deviation of the AR(1) noise.

        Outputs:
            np.ndarray: One value per quarter in ``quarters``.
        """
        # Place each annual anchor at the year's mid-point in quarter units.
        x_anchor = np.arange(len(levels)) * 4.0 + 1.5
        # Interpolate linearly at every quarter.
        base = np.interp(np.arange(len(quarters)), x_anchor, np.asarray(levels, dtype=float))
        # Draw the AR(1) noise with persistence 0.6.
        noise = np.zeros(len(quarters))
        # Recurse the AR(1): e_t = 0.6 e_{t-1} + u_t.
        for k in range(1, len(quarters)):
            # Update the noise.
            noise[k] = 0.6 * noise[k - 1] + rng.normal(0.0, scale)
        # Return the noisy path.
        return base + noise

    # Build the global series once (they are common to every market's rows).
    global_series = {
        name: path(levels, 0.06 if name.startswith("y_") else 0.04 * np.mean(levels))
        for name, levels in anchors.items()
    }
    # Build the domestic series once per economy.
    domestic_series = {
        economy: {name: path(levels, 0.15) for name, levels in series.items()}
        for economy, series in domestic.items()
    }
    # Collect the rows.
    rows: List[Dict[str, Any]] = []
    # Walk the quarters.
    for k, quarter in enumerate(quarters):
        # Date the calendar quarter end.
        period_end = quarter.end_time.normalize()
        # Walk the markets.
        for market, (economy, local_30, local_10) in market_economy.items():
            # Read the domestic CPI of the market.
            cpi = float(domestic_series[economy]["cpi_yoy"][k])
            # Assemble the row with every global series.
            row = {
                "cal_quarter": f"{quarter.year}Q{quarter.quarter}",
                "market_id": market,
                "cal_period_end": period_end,
                "publication_date": period_end + pd.Timedelta(days=int(rng.integers(20, 35))),
                "vintage": "initial_release",
                "flag_macro_revision_applied": 0,
            }
            # Write every global series value.
            row.update({name: float(values[k]) for name, values in global_series.items()})
            # Resolve the local 30-year accessor.
            row["y_30_local"] = row[local_30]
            # Write the domestic macro series.
            row.update(
                {
                    "cpi_yoy": cpi,
                    "ppi_yoy": cpi + float(rng.normal(0.5, 1.5)),
                    "industrial_production_yoy": float(
                        domestic_series[economy]["real_gdp_growth_yoy"][k]
                    )
                    * 1.4
                    + float(rng.normal(0.0, 1.0)),
                    "unemployment_rate": float(domestic_series[economy]["unemployment_rate"][k]),
                    "real_gdp_growth_yoy": float(
                        domestic_series[economy]["real_gdp_growth_yoy"][k]
                    ),
                }
            )
            # Term spread: local y_30 minus the 3-month bill (the schema's only 3-month tenor).
            row["term_spread_30_3m"] = row["y_30_local"] - row["y_3m_us"]
            # Derive the real 10-year yield: y_10 (local) minus CPI YoY.
            row["real_yield_10"] = row[local_10] - cpi
            # Store the row.
            rows.append(row)
    # Assemble and type the panel.
    macro = pd.DataFrame(rows)
    # Return the panel with the revision flag and the two dates typed as the L2 schema declares.
    return macro.astype(
        {
            "flag_macro_revision_applied": "int64",
            "cal_period_end": "datetime64[ns]",
            "publication_date": "datetime64[ns]",
        }
    )
```

#### **Step 1.8: `index_membership` (L4a) and `classifications`**

```python
def generate_index_membership(firms: pd.DataFrame) -> pd.DataFrame:
    """
    Generate the L4a raw index membership history (effective-dated constituent windows).

    Purpose:
        Eliminates survivorship bias: firms are retained only while genuine
        constituents, and the extract contains delistings and acquisitions.

    Inputs:
        firms (pd.DataFrame): The registry from build_firm_registry.

    Processes:
        Writes one interval per issuer; ongoing members keep a null exit date
        (never a sentinel), and every interval is unique per issuer and index.

    Outputs:
        pd.DataFrame: index_name, issuer_id, entry_date, exit_date, exit_reason,
        methodology_version, membership_interval_unique, source_extract_date.

    Raises:
        ValueError: If the registry lacks membership attributes.
    """
    # Name the registry attributes the membership reads.
    required = {"market", "issuer_id", "entry_date", "exit_date", "exit_reason"}
    # Refuse a registry that lacks them.
    if not required.issubset(firms.columns):
        # Name the missing attributes.
        raise ValueError(f"the firm registry lacks {sorted(required - set(firms.columns))}.")
    # Map each market to its methodology version label.
    methodology = {
        "SP500": "SPDJI-2017.2",
        "RUSSELL2000": "FTSE-Russell-2016.1",
        "STOXX600": "STOXX-2016.3",
        "FTSE_APAC_EX_JP": "FTSE-GEIS-2016.2",
        "CSI300": "CSI-2016.1",
    }
    # Assemble one interval per issuer.
    membership = pd.DataFrame(
        {
            "index_name": firms["market"].map(lambda market: MARKETS[market]["index_name"]),
            "issuer_id": firms["issuer_id"],
            "entry_date": firms["entry_date"],
            "exit_date": firms["exit_date"],
            "exit_reason": firms["exit_reason"],
            "methodology_version": firms["market"].map(methodology),
            "membership_interval_unique": True,
            "source_extract_date": EXTRACT_DATE,
        }
    )
    # Return the panel typed as the L4a schema declares.
    return membership.astype(
        {
            "entry_date": "datetime64[ns]",
            "exit_date": "datetime64[ns]",
            "source_extract_date": "datetime64[ns]",
        }
    )
```

```python
def generate_classifications(firms: pd.DataFrame) -> pd.DataFrame:
    """
    Generate the GICS classification history (the fifth raw panel run_task_36 requires).

    Purpose:
        Lets Task 6 date each firm-quarter's sector by an as-of join on the
        effective date, so the 2018 Communication Services reconstitution is
        dated rather than applied with hindsight.

    Inputs:
        firms (pd.DataFrame): The registry from build_firm_registry.

    Processes:
        Writes one vintage per issuer effective 1999-08-01 and a second vintage
        effective 2018-09-28 for the reclassified firms.

    Outputs:
        pd.DataFrame: issuer_id, gics_sector_name, gics_sector_code,
        gics_classification_effective_date.

    Raises:
        ValueError: If the registry lacks sector attributes.
    """
    # Refuse a registry without the sector attributes.
    if not {"issuer_id", "gics_sector_name", "gics_sector_code"}.issubset(firms.columns):
        # Name the missing attributes.
        raise ValueError("the firm registry lacks its GICS attributes.")
    # Write the original vintage of every issuer.
    original = firms.loc[:, ["issuer_id", "gics_sector_name", "gics_sector_code"]].assign(
        gics_classification_effective_date=pd.Timestamp("1999-08-01")
    )
    # Write the 2018 Communication Services vintage of the reclassified issuers.
    reclassified = firms.loc[firms["reclassified_2018"], ["issuer_id"]].assign(
        gics_sector_name="Communication Services",
        gics_sector_code="50",
        gics_classification_effective_date=pd.Timestamp("2018-09-28"),
    )
    # Stack and sort the history.
    history = pd.concat([original, reclassified], ignore_index=True).sort_values(
        ["issuer_id", "gics_classification_effective_date"], ignore_index=True
    )
    # Type the effective date in nanoseconds, as the firm panel's dates are (Task 6 as-of join).
    return history.astype({"gics_classification_effective_date": "datetime64[ns]"})
```

#### **Step 1.9: One call for all five panels**

```python
def generate_mufasa_raw_panels(seed: int = DGP_SEED) -> Dict[str, pd.DataFrame]:
    """
    Generate the five raw panels run_task_36 requires, from one seeded generator.

    Purpose:
        Single entry point of Step 1: fundamental_quarter, macro_quarter,
        index_daily, index_membership and classifications.

    Inputs:
        seed (int): Seed of NumPy's PCG64 generator. Default DGP_SEED.

    Processes:
        Builds the firm registry, the index paths, the firm panel from both,
        the macro panel, the membership history and the classification history.

    Outputs:
        Dict[str, pd.DataFrame]: The five panels keyed as RAW_PANELS_TASK_36.

    Raises:
        TypeError: If seed is not an integer.
    """
    # Refuse a non-integer seed (a bool is not a seed).
    if isinstance(seed, bool) or not isinstance(seed, int):
        # Name the malformed seed.
        raise TypeError(f"seed must be an int; got {type(seed).__name__}.")
    # Open the seeded PCG64 generator.
    rng = np.random.default_rng(seed)
    # Build the static firm registry.
    firms = build_firm_registry(rng)
    # Generate the daily index panel.
    index_daily = generate_index_daily(rng)
    # Return the five panels.
    return {
        "fundamental_quarter": generate_fundamental_quarter(firms, index_daily, rng),
        "macro_quarter": generate_macro_quarter(rng),
        "index_daily": index_daily,
        "index_membership": generate_index_membership(firms),
        "classifications": generate_classifications(firms),
    }
```

### **Step 2: Loading the Configuration (`config.yaml`) and Conforming the Panels**

`config.yaml` is the single source of truth for every convention and threshold. The loader below reads it with `yaml.safe_load`, which yields exactly the plain dictionaries, lists and scalars the stages accept, and it refuses a stored `environment` block, because that block must describe the machine that actually executes the run. The second function makes the firm panel honour `config["validation"]["fundamental_schema"]`: Task 2 compares the column sets in both directions and the dtypes one by one, so the declared column order and dtypes are applied here and any discrepancy is named before the run starts.

```python
# ==============================================================================
# Step 2 — load config.yaml and conform the panels to its declared schema
# ==============================================================================

# Name the blocks run_task_36's stages read from the configuration.
REQUIRED_BLOCKS: Tuple[str, ...] = (
    "validation",
    "market_structure",
    "cleaning",
    "macro",
    "pipeline",
    "baselines",
    "evaluation",
    "ablation",
    "memory_ablation",
    "sensitivity",
    "robustness",
    "packaging",
)
```

```python
def load_study_configuration(filepath: str = "config.yaml") -> Dict[str, Any]:
    """
    Load config.yaml from the working directory into the plain dictionary ``config``.

    Purpose:
        Reads every study parameter of the MUFASA reproduction, so no stage
        relies on an implicit default.

    Inputs:
        filepath (str): Path of the YAML file. Default "config.yaml".

    Processes:
        1. Parses the file with yaml.safe_load (plain dicts, lists and scalars,
           which is the form study_config.json carries and the stages accept).
        2. Requires a mapping holding the twelve operational blocks.
        3. Refuses a hand-written ``environment`` block: run_task_36 needs the
           block measured from the executing run (Step 3 builds it).

    Outputs:
        Dict[str, Any]: The configuration dictionary.

    Raises:
        TypeError: If filepath is not a string or the document is not a mapping.
        FileNotFoundError: If the file does not exist.
        KeyError: If an operational block is missing.
        ValueError: If the file already carries an ``environment`` block.
        yaml.YAMLError: If the YAML is malformed.
    """
    # Refuse a non-string path.
    if not isinstance(filepath, str):
        # Name the malformed argument.
        raise TypeError(f"filepath must be a str; got {type(filepath).__name__}.")
    # Resolve the path against the working directory.
    path = Path(filepath)
    # Refuse a missing file explicitly, never falling back to an empty configuration.
    if not path.is_file():
        # Name the missing file.
        raise FileNotFoundError(
            f"{path.resolve()} does not exist; save config.yaml in the working directory."
        )
    # Parse the YAML document safely.
    with path.open("r", encoding="utf-8") as handle:
        # Read the mapping.
        loaded = yaml.safe_load(handle)
    # Refuse a document that is not a mapping.
    if not isinstance(loaded, dict):
        # Name the malformed document.
        raise TypeError(f"{path} must hold a mapping; got {type(loaded).__name__}.")
    # List the operational blocks the document lacks.
    missing = [block for block in REQUIRED_BLOCKS if block not in loaded]
    # Refuse an incomplete configuration.
    if missing:
        # Name every missing block.
        raise KeyError(f"config.yaml lacks the operational blocks {missing}.")
    # Refuse a stored environment block, which would claim unmeasured provenance.
    if "environment" in loaded:
        # Name the forbidden block.
        raise ValueError("config.yaml must not carry 'environment'; it is measured at run time.")
    # Return the configuration.
    return loaded
```

```python
def conform_panels_to_schema(
    panels: Mapping[str, pd.DataFrame], config: Mapping[str, Any]
) -> Dict[str, pd.DataFrame]:
    """
    Conform the firm panel to config.validation.fundamental_schema before Task 2 validates it.

    Purpose:
        Task 2 checks the two-way column set difference and dtype equality
        against the declared schema; this step makes the synthetic extract
        honour that contract and fails early, with every offence named, when
        it cannot.

    Inputs:
        panels (Mapping[str, pd.DataFrame]): The five raw panels.
        config (Mapping[str, Any]): The loaded configuration.

    Processes:
        1. Requires exactly the five panel names of RAW_PANELS_TASK_36.
        2. Requires every declared fundamental column, orders the columns as
           declared and casts each to its declared dtype.
        3. Requires the macro panel to hold every declared macro series and a
           row for every market of config.pipeline.index_to_market.

    Outputs:
        Dict[str, pd.DataFrame]: The five panels, the firm panel conformed.

    Raises:
        KeyError: If a panel or a declared column is missing.
        ValueError: If a market has no macro row or a cast fails.
    """
    # Name the panels the driver requires (the notebook's own constant).
    expected = list(RAW_PANELS_TASK_36)
    # Refuse a panel set that differs from the driver's contract.
    if sorted(panels) != sorted(expected):
        # Name both sets.
        raise KeyError(f"panels must be exactly {expected}; got {sorted(panels)}.")
    # Read the declared firm-panel schema.
    schema = config["validation"]["fundamental_schema"]
    # Read the declared columns in order.
    columns: List[str] = list(schema["columns"])
    # Take a copy of the firm panel.
    fundamental = panels["fundamental_quarter"].copy()
    # List the declared columns the extract lacks.
    absent = [column for column in columns if column not in fundamental.columns]
    # Refuse an extract that lacks declared columns.
    if absent:
        # Name every absent column.
        raise KeyError(f"fundamental_quarter lacks the declared columns {absent}.")
    # Keep exactly the declared columns in the declared order.
    fundamental = fundamental.loc[:, columns]
    # Cast every column to its declared dtype.
    for column, dtype in schema["dtypes"].items():
        # Attempt the cast and name the column on failure.
        try:
            # Cast the column.
            fundamental[column] = fundamental[column].astype(dtype)
        except (TypeError, ValueError) as error:
            # Name the column and the dtype.
            raise ValueError(
                f"fundamental_quarter[{column!r}] cannot be cast to {dtype}: {error}"
            ) from error
    # Read the macro panel.
    macro = panels["macro_quarter"]
    # List the declared macro series the panel lacks.
    missing_series = [
        s for s in config["validation"]["macro_schema"]["series_columns"] if s not in macro.columns
    ]
    # Refuse a macro panel that lacks declared series.
    if missing_series:
        # Name the missing series.
        raise KeyError(f"macro_quarter lacks the declared series {missing_series}.")
    # Read the market labels of the pipeline.
    markets = set(config["pipeline"]["index_to_market"].values())
    # List the markets without a macro row.
    uncovered = sorted(markets - set(macro["market_id"].astype(str)))
    # Refuse an uncovered market.
    if uncovered:
        # Name the uncovered markets.
        raise ValueError(f"macro_quarter holds no row for the markets {uncovered}.")
    # Return the five panels with the conformed firm panel.
    return {**dict(panels), "fundamental_quarter": fundamental}
```

The interface's own defaults and the principal settings stored in `config.yaml` can be printed directly from the live objects:

```python
# Import inspect to read run_task_36's own signature and defaults.
import inspect

# Read config.yaml into the dictionary `config` (Step 2's loader).
config = load_study_configuration("config.yaml")
# Read the live signature of the study interface.
signature = inspect.signature(run_task_36)
# Print every parameter with its kind and its default (or "required").
for name, parameter in signature.parameters.items():
    # Render the default, marking parameters that have none.
    default = (
        "required" if parameter.default is inspect.Parameter.empty else repr(parameter.default)
    )
    # Print the parameter's name, kind and default.
    print(f"{name:>12} | {parameter.kind.name:<20} | {default}")
# Collect the config.yaml settings the stages read, with their stored values.
pipeline = config["pipeline"]
# Tabulate the principal operational settings.
defaults_table = pd.DataFrame(
    [
        ("pipeline.train_fraction", pipeline["train_fraction"]),
        ("pipeline.embargo_quarters", pipeline["embargo_quarters"]),
        ("pipeline.fit_fraction", pipeline["fit_fraction"]),
        ("pipeline.max_iterations", pipeline["max_iterations"]),
        ("pipeline.coordinator_iterations", pipeline["coordinator_iterations"]),
        ("pipeline.retrieval_top_k", pipeline["retrieval_top_k"]),
        ("pipeline.min_cell_occupancy", pipeline["min_cell_occupancy"]),
        ("pipeline.memory_cap", pipeline["memory_cap"]),
        ("pipeline.differential_evolution", pipeline["differential_evolution"]),
        ("pipeline.serving.model_id", pipeline["serving"]["model_id"]),
        ("evaluation.alpha", config["evaluation"]["alpha"]),
        (
            "reproducibility.seed_values",
            config["study_specification"]["reproducibility"]["seed_values"],
        ),
    ],
    columns=["setting", "value"],
)
# Print the table.
print(defaults_table.to_string(index=False))
```

**Observed output** (pandas' right-alignment padding of the `value` column condensed):

```text
      config | POSITIONAL_OR_KEYWORD | required
      panels | POSITIONAL_OR_KEYWORD | required
  output_dir | POSITIONAL_OR_KEYWORD | required
    registry | KEYWORD_ONLY         | None
       seeds | KEYWORD_ONLY         | required
    services | KEYWORD_ONLY         | None
        skip | KEYWORD_ONLY         | ()
   data_mode | KEYWORD_ONLY         | 'licensed'
      resume | KEYWORD_ONLY         | True
                        setting   value
        pipeline.train_fraction   0.8
      pipeline.embargo_quarters   1
          pipeline.fit_fraction   0.9
        pipeline.max_iterations   50
pipeline.coordinator_iterations   30
       pipeline.retrieval_top_k   20
    pipeline.min_cell_occupancy   200
            pipeline.memory_cap   500
pipeline.differential_evolution   {'population_multiplier': 15, 'generations_max': 200,
                                   'crossover_rate': 0.7, 'differential_weight': 0.5,
                                   'parameter_bounds': [-1000000.0, 1000000.0],
                                   'early_stop_patience': 20, 'early_stop_tolerance': 1e-06,
                                   'admissible_share_floor': 0.5}
      pipeline.serving.model_id   Qwen/Qwen3-4B-Thinking
               evaluation.alpha   0.05
    reproducibility.seed_values   [11, 23, 41, 67, 101]
```

### **Step 3: Composing the Arguments of `run_task_36`**

`prepare_run_inputs` derives every keyword argument without inventing a value. The seeds come from `config.yaml`. The `environment` block is measured by `collect_provenance_task_36` (interpreter, package versions and record digests, input digests) and overlaid on the notebook's `STUDY_ENVIRONMENT_DECLARATION` by `build_environment_task_36`, so Task 1 records what really executed. The registry is built from the notebook's own `run_task_1` … `run_task_35`. A licensed run is refused here because it needs the operator's served model (`config["pipeline"]["serving"]["model_id"] = "Qwen/Qwen3-4B-Thinking"`), sentence encoder and tokenizer, which no stand-in may replace.

`config.yaml`'s budgets make a full run a multi-day job: 50 agent iterations (Algorithm 1) and 30 coordinator iterations (Algorithm 2) per seed, 200 differential-evolution generations, 500-tree forests, five seeds, and about 29 nested pipeline re-runs inside the ablation, memory-ablation, sensitivity and robustness stages (Tasks 30–34). `make_smoke_configuration` therefore builds a separate, clearly labelled copy that shrinks **only** those budgets so that all 35 stages can be exercised in minutes. It changes no method, threshold, schema or table setting, and its results must never be reported as study results.

```python
# ==============================================================================
# Step 3 — compose the run's inputs and call run_task_36
# ==============================================================================

# Root the run directories under a short path: Tasks 30-34 nest whole pipeline runs, and
# Windows refuses paths longer than 260 characters unless long paths are enabled.
RUN_ROOT: Path = Path.home() / "mufasa_runs"
# Name the directory of the full study run.
STUDY_OUTPUT_DIR: str = str(RUN_ROOT / "study")
# Name the directory of the time-boxed smoke run.
SMOKE_OUTPUT_DIR: str = str(RUN_ROOT / "smoke")
```

```python
def prepare_run_inputs(
    config: Mapping[str, Any], panels: Mapping[str, pd.DataFrame], data_mode: str = "synthetic"
) -> Dict[str, Any]:
    """
    Compose every argument of run_task_36 from the configuration and the panels.

    Purpose:
        Builds, without inventing any value, the measured environment block, the
        orchestrator registry, the seeds and the services the driver needs.

    Inputs:
        config (Mapping[str, Any]): The configuration loaded from config.yaml.
        panels (Mapping[str, pd.DataFrame]): The five conformed raw panels.
        data_mode (str): "synthetic" for fabricated panels, "licensed" for the
            vendor extract. Default "synthetic".

    Processes:
        1. Reads the seeds from study_specification.reproducibility.seed_values.
        2. Measures provenance from the executing run (collect_provenance_task_36)
           and composes Task 1's environment over the declared environment
           (build_environment_task_36 with STUDY_ENVIRONMENT_DECLARATION).
        3. Builds the registry {n: run_task_n} from the notebook's own functions.
        4. Selects the declared stand-in services for a synthetic run; a licensed
           run requires the operator's served model, encoder and tokenizer.

    Outputs:
        Dict[str, Any]: config (with environment), seeds, registry, services,
        provenance and data_mode.

    Raises:
        ValueError: If data_mode is undeclared, the seeds are malformed, or a
            licensed run is requested without operator services.
    """
    # Refuse an undeclared data mode (the notebook's own constant).
    if data_mode not in DATA_MODES_TASK_36:
        # Name the declared modes.
        raise ValueError(
            f"data_mode must be one of {list(DATA_MODES_TASK_36)}; got {data_mode!r}."
        )
    # Read the reproduction seeds declared in the configuration.
    seeds = [int(seed) for seed in config["study_specification"]["reproducibility"]["seed_values"]]
    # Refuse an empty or repeated seed list.
    if not seeds or len(set(seeds)) != len(seeds):
        # Name the malformed list.
        raise ValueError(f"the seed list must be non-empty and distinct; got {seeds}.")
    # Measure the provenance of exactly these inputs (commit, digests, interpreter, packages).
    provenance = collect_provenance_task_36(config, panels)
    # Compose Task 1's environment: the declaration overlaid with the measured values.
    environment = build_environment_task_36(STUDY_ENVIRONMENT_DECLARATION, provenance, seeds)
    # Merge the environment into a copy of the configuration.
    run_config = {**copy.deepcopy(dict(config)), "environment": environment}
    # Build the registry from the notebook's own orchestrators (Tasks 1 to 35).
    registry = {task: globals()[f"run_task_{task}"] for task in range(1, 36)}
    # Refuse a licensed run without operator services: no stand-in replaces the method.
    if data_mode == "licensed":
        # Name what the operator must supply.
        raise ValueError(
            "a licensed run needs services={'embed_fn', 'tokenizer', 'role_callables', "
            "'llm_client', 'funsearch_client', 'llm_sr_client'} from the operator."
        )
    # Take the declared stand-ins of a synthetic verification run.
    services = standin_services_task_36()
    # Return the composed arguments.
    return {
        "config": run_config,
        "seeds": seeds,
        "registry": registry,
        "services": services,
        "provenance": provenance,
        "data_mode": data_mode,
    }
```

```python
def make_smoke_configuration(config: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Return a time-boxed copy of the configuration for a pipeline smoke test.

    Purpose:
        config.yaml's budgets (50 agent iterations, 30 coordinator iterations,
        200 differential-evolution generations, 500 trees, and ~29 full pipeline
        re-runs inside Tasks 30-34 per seed) make a complete run a multi-day job.
        This copy shrinks ONLY the search and training budgets so the wiring of
        all 35 stages can be verified in minutes. It is NOT the study
        configuration and its results must never be reported as study results.

    Inputs:
        config (Mapping[str, Any]): The configuration loaded from config.yaml.

    Processes:
        Deep-copies the configuration and overwrites eight budget settings;
        every method, threshold, schema and published-table setting is unchanged.

    Outputs:
        Dict[str, Any]: The smoke-test configuration.

    Raises:
        KeyError: If a budget setting's block is missing.
    """
    # Deep-copy, so config.yaml's dictionary is never altered.
    smoke = copy.deepcopy(dict(config))
    # Shrink Algorithm 1's iterations per agent and Algorithm 2's per context.
    smoke["pipeline"].update({"max_iterations": 2, "coordinator_iterations": 2})
    # Shrink the differential-evolution generation budget and its patience.
    smoke["pipeline"]["differential_evolution"].update(
        {"generations_max": 15, "early_stop_patience": 5}
    )
    # Shrink the random forest and the gradient-boosting iterations.
    smoke["baselines"]["ml"]["rf"]["n_estimators"] = 20
    # Shrink the histogram gradient booster's iterations.
    smoke["baselines"]["ml"]["histgbm"]["max_iter"] = 20
    # Shrink the network's epoch budget.
    smoke["baselines"]["ml"]["nn"]["max_epochs"] = 5
    # Shrink the FunSearch and LLM-SR budgets.
    smoke["baselines"]["symbolic"]["budgets"] = {"funsearch": 2, "llm_sr": 2}
    # Return the smoke-test configuration.
    return smoke
```

```python
def execute_study(
    inputs: Mapping[str, Any],
    panels: Mapping[str, pd.DataFrame],
    output_dir: str = "mufasa_study_run",
    skip: Sequence[int] = (),
    resume: bool = True,
) -> Dict[str, Any]:
    """
    Run the whole pipeline through run_task_36 and return its result, completed or not.

    Purpose:
        Calls the study interface once and, when the run does not complete,
        returns the result the driver attached to Task36NotCompletedError so
        every stage record can be inspected.

    Inputs:
        inputs (Mapping[str, Any]): The output of prepare_run_inputs.
        panels (Mapping[str, pd.DataFrame]): The five conformed raw panels.
        output_dir (str): The run's output directory. Default "mufasa_study_run".
        skip (Sequence[int]): Driver stages declared skipped in advance. Default ().
        resume (bool): Resume driver stages whose checkpoint matches. Default True.

    Processes:
        1. Calls run_task_36(config, panels, output_dir, registry=..., seeds=...,
           services=..., skip=..., data_mode=..., resume=...).
        2. Catches Task36NotCompletedError and returns its ``result``.

    Outputs:
        Dict[str, Any]: The driver's result (status, records, outputs, order,
        manifest_path, failure_ledger_path, run_id, data_mode, skipped,
        loader_mode, seeds).

    Raises:
        ValueError: Propagated from run_task_36 on malformed arguments.
    """
    # Call the study interface.
    try:
        # Run the 35-stage plan in dependency order.
        return run_task_36(
            inputs["config"],
            dict(panels),
            output_dir,
            registry=inputs["registry"],
            seeds=inputs["seeds"],
            services=inputs["services"],
            skip=tuple(skip),
            data_mode=inputs["data_mode"],
            resume=resume,
        )
    except Task36NotCompletedError as error:
        # Report the driver's own summary of the incomplete run.
        print(f"run_task_36 did not complete: {error}")
        # Return the assembled result the driver attached to the error.
        return dict(error.result)
```

### **Step 4: Running the Pipeline and Reading the Three Institutional Assets**

```python
# ==============================================================================
# Step 4 — inspect the driver's result and the three institutional assets
# ==============================================================================
```

```python
def summarise_study_result(result: Mapping[str, Any], data_mode: str) -> Dict[str, Any]:
    """
    Tabulate the stage records and extract the study's three institutional assets.

    Purpose:
        Turns run_task_36's result into the artefacts a reviewer reads: the
        per-stage status table, the published study status, the fitted
        closed-form equations, the context-indexed weight matrix of Equation (4)
        and the per-hypothesis seven-family reliability profiles.

    Inputs:
        result (Mapping[str, Any]): The mapping run_task_36 returned (or
            attached to Task36NotCompletedError).
        data_mode (str): The data mode the run used.

    Processes:
        1. Builds a DataFrame of the stage records in execution order.
        2. Maps (driver status, data mode) to the published study status through
           STUDY_STATUSES_TASK_36 (only completed runs have a published status).
        3. Reads Task 22's run artefacts of the first registry seed: fitted
           expressions, weight matrix and reliability profiles.

    Outputs:
        Dict[str, Any]: records, study_status, expressions, weight_matrix,
        reliability_profiles (the last three None when Task 22 did not complete).

    Raises:
        KeyError: If the result lacks the driver's declared keys.
    """
    # Name the keys every driver result carries.
    declared = ("status", "records", "outputs", "order", "manifest_path", "run_id", "seeds")
    # Refuse a mapping that is not a driver result.
    missing = [key for key in declared if key not in result]
    # Halt on a malformed result.
    if missing:
        # Name the missing keys.
        raise KeyError(f"the result lacks the driver keys {missing}.")
    # Tabulate the stage records in execution order.
    records = pd.DataFrame(result["records"]).loc[
        :, ["task", "callable", "role", "status", "n_calls", "seconds", "reason"]
    ]
    # Map the driver status and the data mode to the published study status.
    study_status = STUDY_STATUSES_TASK_36.get((result["status"], data_mode), "not_published")
    # Read Task 22's outputs, when the stage completed.
    task_22 = result["outputs"].get(22) or {}
    # Read the per-seed run artefacts.
    runs = task_22.get("runs") or {}
    # Read the first registry seed's artefacts.
    run = runs.get(result["seeds"][0]) if runs else None
    # Return the summary.
    return {
        "records": records,
        "study_status": study_status,
        "expressions": None if run is None else run.fitted_expressions,
        "weight_matrix": None if run is None else run.weight_matrix,
        "reliability_profiles": None if run is None else run.reliability_profiles,
    }
```

#### **Step 4.1: The study call at `config.yaml` scale**

This is the complete invocation at the configuration's own budgets, for all five seeds, with nothing skipped. It is shown for completeness and was **not** run to completion during verification (it takes days on a workstation).

```python
# Generate the five raw panels from the seeded data-generating process.
raw_panels = generate_mufasa_raw_panels()
# Read config.yaml from the working directory into the dictionary `config`.
config = load_study_configuration("config.yaml")
# Conform the firm panel to config.validation.fundamental_schema.
panels = conform_panels_to_schema(raw_panels, config)
# Compose run_task_36's arguments: measured environment, registry, five seeds, stand-in services.
study_inputs = prepare_run_inputs(config, panels, data_mode="synthetic")
# Run all 35 stages at config.yaml's budgets, for every registry seed (a multi-day job).
study_result = execute_study(
    study_inputs, panels, output_dir=STUDY_OUTPUT_DIR, skip=(), resume=True
)
# Summarise the run and its three institutional assets.
study_summary = summarise_study_result(study_result, study_inputs["data_mode"])
# Report the driver status and the published study status.
print(study_result["status"], "->", study_summary["study_status"])
```

#### **Step 4.2: The time-boxed smoke call (executed)**

The same interface, the same panels and the same `config.yaml`, with the smoke budgets and the first seed only. Running every stage end to end is the purpose of this cell.

```python
# Generate the five raw panels from the seeded data-generating process.
raw_panels = generate_mufasa_raw_panels()
# Report each panel's shape.
for panel_name, frame in raw_panels.items():
    # Print the panel name and its (rows, columns).
    print(f"{panel_name:>20}: {frame.shape}")
# Read config.yaml from the working directory into the dictionary `config`.
config = load_study_configuration("config.yaml")
# Conform the firm panel to config.validation.fundamental_schema.
panels = conform_panels_to_schema(raw_panels, config)
# Build the time-boxed copy (budgets only) for the smoke test.
smoke_config = make_smoke_configuration(config)
# Compose run_task_36's arguments for a synthetic run.
smoke_inputs = prepare_run_inputs(smoke_config, panels, data_mode="synthetic")
# Restrict the smoke test to the first registry seed.
smoke_inputs["seeds"] = smoke_inputs["seeds"][:1]
# Rebuild the environment block so Task 1 records exactly the seeds that run.
smoke_inputs["config"]["environment"] = build_environment_task_36(
    STUDY_ENVIRONMENT_DECLARATION, smoke_inputs["provenance"], smoke_inputs["seeds"]
)
# Run all 35 stages through the study interface.
smoke_result = execute_study(smoke_inputs, panels, output_dir=SMOKE_OUTPUT_DIR)
# Summarise the run and its three institutional assets.
smoke_summary = summarise_study_result(smoke_result, smoke_inputs["data_mode"])
# Report the driver status and the published study status.
print(smoke_result["status"], "->", smoke_summary["study_status"])
# Show the per-stage records.
print(smoke_summary["records"].to_string(index=False))
```

Output of the executed smoke cell (seed 11, synthetic panels, smoke budgets). The three diagnostic lines are written to standard error and may appear in a different position in your console:

```text
 fundamental_quarter: (5760, 79)
       macro_quarter: (265, 30)
         index_daily: (19879, 12)
    index_membership: (125, 8)
     classifications: (127, 4)
completed -> pipeline_verified_on_synthetic_data
 task    callable                    role    status  n_calls    seconds                                 reason
    1  run_task_1                  driver completed        1   0.280175                               executed
    2  run_task_2                  driver completed        1   1.477954                               executed
    3  run_task_3                  driver completed        1   1.446512                               executed
    4  run_task_4                  driver completed        1   2.266095                               executed
   22 run_task_22                  driver completed        1  35.853263                               executed
    5  run_task_5          within_task_22 completed        0   0.000091                executed inside Task 22
    6  run_task_6          within_task_22 completed        0   0.000031                executed inside Task 22
    7  run_task_7          within_task_22 completed        0   0.000027                executed inside Task 22
    8  run_task_8          within_task_22 completed        0   0.000021                executed inside Task 22
    9  run_task_9          within_task_22 completed        0   0.000023                executed inside Task 22
   10 run_task_10          within_task_22 completed        0   0.000020                executed inside Task 22
   11 run_task_11          within_task_22 completed        0   0.000021                executed inside Task 22
   12 run_task_12          within_task_22 completed        0   0.000021                executed inside Task 22
   15 run_task_15          within_task_22 completed        0   0.000058                executed inside Task 22
   13 run_task_13 collaborator_of_task_15 completed        0   0.000011 called inside Task 15's discovery loop
   14 run_task_14 collaborator_of_task_15 completed        0   0.000021 called inside Task 15's discovery loop
   16 run_task_16 collaborator_of_task_15 completed        0   0.000006 called inside Task 15's discovery loop
   17 run_task_17 collaborator_of_task_15 completed        0   0.000005 called inside Task 15's discovery loop
   18 run_task_18 collaborator_of_task_15 completed        0   0.000005 called inside Task 15's discovery loop
   19 run_task_19 collaborator_of_task_15 completed        0   0.000005 called inside Task 15's discovery loop
   20 run_task_20          within_task_22 completed        0   0.000024                executed inside Task 22
   21 run_task_21          within_task_22 completed        0   0.000022                executed inside Task 22
   23 run_task_23                  driver completed        1   7.493838                               executed
   24 run_task_24                  driver completed        5   5.757943                               executed
   25 run_task_25                  driver completed        1   4.822049                               executed
   26 run_task_26                  driver completed        1   2.440786                               executed
   27 run_task_27                  driver completed        1   5.352807                               executed
   28 run_task_28                  driver completed        1  10.705338                               executed
   29 run_task_29                  driver completed        1   4.598364                               executed
   30 run_task_30                  driver completed        1 185.789695                               executed
   31 run_task_31                  driver completed        1 160.598019                               executed
   32 run_task_32                  driver completed        1  97.255489                               executed
   33 run_task_33                  driver completed        1 248.503123                               executed
   34 run_task_34                  driver completed        1 530.330185                               executed
   35 run_task_35                  driver completed        1   3.098169                               executed
```

The diagnostics are expected and do not change the status:

- **`fit_hash` divergence.** The feature-policy object passed between stages carries a hash that differs from its recomputed statistics. The stage uses the statistics and records the divergence; it does not stop.
- **`fincon` and `finvision` unavailable.** These external agent frameworks publish no forecasting entry point. The comparison records them as unavailable unless the operator declares `config['framework_entry_points'][<name>] = "package.module:function"`.

The records show the execution plan: driver stages 1–4, then Task 22, then 23–35. Task 22 runs stages 5–12, 15, 20 and 21 for each seed. Task 15 calls 13, 14 and 16–19 inside its discovery loop. Those inner stages therefore show `n_calls = 0` and almost no time of their own, because their time is counted inside Task 22.

The fitted equations of the five perspective agents in the same run, printed in full by the next cell, are shown here on one line each. They are **pipeline output on synthetic data under smoke budgets**, not findings of the study.

```text
expression asset : (0.0010193979256846555 * Revenue_ps)
expression cashflow : ((-0.0032221505610975027) * NI_ps)
expression earnings : ((-0.0032225940300549157) * NI_ps)
expression growth : ((-9.601220742308452e-07) * (Revenue_ps * ((-1075.4418052499834) + (SALES_REV_TURN_YOY / (-2.8617740056700844)))))
expression quality : (0.7983762484376477 * (NI_ps * P_FCF))
```

Inspecting the assets of the first seed, and comparing every model on the same rows. Task 27's table carries, beside each model's MAPE on its own scored rows (`pooled`, `n_scored`), the MAPE on the common support (`common_pooled`, `n_common`): the rows of a market that every scored model covers. Task 29 writes the same comparison as a market-by-model matrix, `table_2_common_support.csv`, beside `table_2.csv`.

```python
# Show the fitted closed-form equation of each perspective agent.
print(smoke_summary["expressions"])
# Show the context-indexed weight matrix of Equation (4).
print(smoke_summary["weight_matrix"])
# Show the seven-family reliability profile of each hypothesis.
print(smoke_summary["reliability_profiles"])
# Locate the run manifest and, if written, the failure ledger.
print(smoke_result["manifest_path"], smoke_result["failure_ledger_path"])
# Read the first registry seed of the run.
first_seed = smoke_result["seeds"][0]
# Read Task 27's MAPE table of that seed.
mape_table = smoke_result["outputs"][27]["metrics"][first_seed]["mape_variants"]
# Keep each model's across-market row.
across = mape_table.loc[mape_table["market"] == ACROSS_MARKETS_TASK_27]
# Compare own-row MAPE with MAPE on the rows every model scores.
print(across[["model", "pooled", "n_scored", "common_pooled", "n_common"]].to_string(index=False))
# Locate Task 29's market-by-model matrix on the common support.
print(smoke_result["outputs"][29]["paths"][first_seed]["table_2_common_support"])
```

The first three `print` calls return the full expression, weight-matrix and reliability-profile objects (the weight matrix of this run has 44 rows, one per market × sector × regime cell, and 18 columns). They are long, so only the output of the last three calls is reproduced:

```text
C:\Users\techuf02l\mufasa_runs\smoke\pipeline_manifest_task_36.json None
                     model    pooled  n_scored  common_pooled  n_common
                    Fin-R1 38.023717      1051       3.090779       721
                     Fino1 38.023717      1051       3.090779       721
                    MUFASA  0.399505      1023       0.446701       721
                 ddm_price  2.305945       773       2.412250       721
          ev_ebit_baseline 84.009721      1021       2.864278       721
        ev_ebitda_baseline 62.712744      1021       2.865142       721
                fcfe_price  8.080611       773       8.482008       721
                fcff_price  9.717675       773      10.229526       721
                 funsearch  0.626416      1033       0.722240       721
                   histgbm 23.486857      1051       6.249318       721
                    llm_sr  0.328420      1033       0.365558       721
naive_cross_sectional_mean 79.468930      1051      54.056229       721
         naive_persistence  0.146033      1051       0.150735       721
               naive_trend  0.359650      1036       0.199775       721
                        nn 45.802176      1051      26.696895       721
               pb_baseline 87.011558      1021       0.743272       721
               pe_baseline 67.634203      1021       0.180284       721
                        rf 13.876682      1051       1.132200       721
C:\Users\techuf02l\mufasa_runs\smoke\task_29\seed_11\table_2_common_support.csv
```

How to read the table:

- **`n_common` is 721 for every model.** That is the number of (quarter, firm) rows, summed over the five markets, that all 18 scored models cover. `pysr` is absent because its back-end is not installed in this environment (Task 24 records it as *unavailable*), and `fincon` and `finvision` are absent for the reason given above.
- **`pooled` and `common_pooled` can differ by an order of magnitude.** Fin-R1 and Fino1 fall from 38.0 on their own 1,051 rows to 3.09 on the common rows, and `pe_baseline` from 67.6 to 0.18. Their largest errors sit on rows that some other model does not score. A ranking of models by `pooled` is therefore partly a ranking of coverage, which is why the common-support column is reported beside it.
- **MUFASA scores 1,023 of 1,051 rows** (coverage 0.973), so its `pooled` figure is also an own-row figure. On the common rows it is 0.447.

### **Corrections made to the notebook**

Building and auditing this example exposed six defects, and an independent assessment of the notebook against the paper exposed six more. Each one is fixed in the notebook. The copy taken before each of the first six fixes is kept in a dated `backup_*` folder; the last six are separate commits on top of the notebook of commit `9b184f7`, so `git` holds every pre-fix state.

**Quarter keys (2026-10-23; pre-fix notebook in `backup_20261023_quarter_key_fix/`).** With vendor fiscal labels such as `"FY2020Q2"`, June filers or a fiscal-year change, each of the following stopped the pipeline. The fixes adopt one quarter key throughout: the **calendar quarter**. That is `cal_quarter` when it parses, and otherwise the calendar quarter that contains `fiscal_period_end`. A fiscal label is never used as a key, because issuers with different fiscal-year ends share one label.

1. **Task 7, validation carve (`carve_validation_task_7`).** The carve ordered each market's keys on the calendar axis but matched rows by the text of `fiscal_quarter_label`. With `"FY…"` labels no row matched, the validation slice was empty, and Task 9 stopped with *no finite winsor bounds*. Rows are now matched through `_axis_quarter_keys_task_7`, the same key the ordering uses.
2. **Task 26, naive baselines (`build_naive_benchmarks_task_26`).** When `cal_quarter` was missing, as on fiscal-year-change rows, the key fell back to parsing the fiscal label as a calendar quarter, which produced duplicate keys. The order of precedence is now `cal_quarter`, then the calendar quarter of `fiscal_period_end`, then the label.
3. **Tasks 23 to 29, one evaluation key (Task 36 wiring).** MUFASA (Task 22) and the language-model baselines (Task 25) keyed their predictions on `cal_quarter`. The actuals and the ML, symbolic and naive baselines (Tasks 23, 24 and 26) keyed theirs on the fiscal label, so Task 27 stopped with *no matched prediction row*. `_evaluation_quarters_task_36` now gives every one of them the calendar-quarter key, and the Gate 6 check that test quarters follow training quarters orders by the same key.

**Coverage and comparability (2026-10-23; pre-fix copies in `backup_20261023_fix_b_c/` and `backup_20261023_task6_task29_usage/`).**

4. **Task 21, contexts first seen in the test window (`run_task_21`).** The weight registry held only training contexts, so a held-out row whose sector × regime never occurred in training received no weight and no MUFASA forecast. Such rows were silently left out of MUFASA's score while every baseline was scored on them. Every held-out context is now declared to the registry. One with no training rows takes its sector pool, or the market pool when its sector is absent from training or below `min_firm_quarters`. Contexts seen in training are unaffected, and the cells concerned are listed in the result's `test_only_cells`.
5. **Tasks 27 and 29, comparison on common rows.** Each MAPE variant averages a model's *own* scored rows, so models with different coverage were compared on different rows.
    - Task 27 now also reports `common_pooled` and `n_common`: the pooled MAPE on the rows of a market that every scored model covers.
    - Task 29 carries the new figure as a fourth variant in its long table (with `n_rows`, the rows each figure averages) and writes `table_2_common_support.csv`.
    - The three original variants, the headline `pooled` and `table_2.csv` are unchanged. The Diebold–Mariano tests of Task 28 already used jointly covered rows only.
6. **Task 6, the pre-2018 GICS sector name (`build_sector_mapping_task_6`).** On 2018-09-28 GICS renamed Telecommunication Services (sector code 50) to Communication Services under the same code. A point-in-time classification history therefore carries the old name for earlier vintages. That name was outside the eleven paper labels, so Task 6 halted. It now maps to *Communications*, the same label as its successor, and the same mapping is recorded under `gics_to_paper_mapping` in `config.yaml` and `study_config.json`. Firms that moved into the sector from Information Technology or Consumer Discretionary in 2018 keep their earlier sector for earlier quarters, as their as-of vintages state.

**Assessed defects (2026-10-23; pre-fix notebook at commit `9b184f7`).** Each correction below has its own targeted check under `verification/`, which must print `CHECK OK`.

7. **Tasks 20 and 21, the weight fit's halt (`fit_perspective_weights_task_21`, `fit_weights_slsqp_task_20`).** A start was accepted only when SLSQP reported success *and* its point was feasible. SLSQP reports a start that stops at a kink of the non-smooth MAPE objective ("Positive directional derivative for linesearch") as unsuccessful although its point is feasible, so a cell whose starts all stopped that way halted the whole run, with a message that called a sub-tolerance violation infeasible. A start is now a candidate when its objective is finite and its point is feasible; the lowest objective wins and a converged start is preferred on a tie. Each start records its convergence flag and solver message, each fit reports `n_converged`, `chosen_converged` and `premature_termination`, Task 21 lists such units in `non_converged_units`, and the halt message counts the true causes. Check: `check_task21_solver.py` (60 seeded difficult cells: 2 halted before the fix on this platform, 0 after).
8. **Tasks 20 → 21, the meta-coordinator's subset and start (`run_task_20`, `_stage_task_20`, `_stage_task_21`, `run_task_21`, `fit_perspective_weights_task_21`).** The specification has the coordinator select a subset $A^*$ of the agents and propose starting weights $\tilde{\mathbf w}^{(0)}$, and SLSQP fit over $A^*$ from $\tilde{\mathbf w}^{(0)}$ (`slsqp_weight_optimiser.initial_point_source: "meta_LLM_proposal"`). Task 21 ignored the coordinator, so its output reached no forecast. Task 20 now publishes every unit's proposal (`per_cell_proposals.json`), Task 22 passes it to Task 21, and Task 21 fits each unit over the proposal's subset (weights proposed above `SIMPLEX_TOLERANCE`), starting from the renormalised proposal; outside the subset the weights are exactly zero. A unit without a proposal is fitted as before. Because MAPE is convex in the weights, the subset is what lets the coordinator change a forecast. Check: `check_task21_coordinator_subset.py`.
9. **Task 22, the meta-coordinator per market (`_stage_task_20`).** Task 20 ran once on every market's predictions, so its contexts were (sector, regime) pooled across markets, whereas the paper's regime is each market's own and each market has its own released weights. The coordinator now runs once per market under `task_20/<market>/`, with the seed `cell_seed_task_20(seed, market)` and its own meta-memory, and its weights, proposals and learnings are labelled `market::…`. A unit that escalates to a pool (too few complete rows) carries the proposal of the pool it resolved to. Check: `check_task20_per_market.py`.
10. **Task 7, the forward target's share basis (`audit_share_basis_task_7`, `build_forward_target_task_7`, `run_task_7`).** The target $y_{i,t+1}$ is the next quarter's price, while every per-share feature divides by the quarter-$t$ share count. In a contemporaneous extract a split between $t$ and $t+1$ puts the target on the new basis, and each row still reconciles its own market capitalisation, so nothing caught it. Two rows whose `px_split_adjustment_reference_date` values are present and equal share one basis; otherwise a share-count change of at least 1.5× with the market-capitalisation ratio inside [0.5, 2] is a break, and its target is dropped (policy `drop`; `adjust` multiplies it by the share ratio). The flagged pairs are written to `share_basis_audit_task_7.csv`, and the constants are registered as `[UNSPECIFIED IN MANUSCRIPT]` decisions. The synthetic panels carry one snapshot reference date, so no pair is flagged there. Check: `check_task7_share_basis.py`.
11. **Task 25, the EV-multiple baselines (`sector_median_baselines_task_25`, `SECTOR_MEDIAN_PAIRS`).** `EBIT_ps × SECTOR_MEDIAN_EV_EBIT` (and EBITDA likewise) is enterprise value per share, a whole-firm claim, yet it was scored against the share price. Net debt per share, `(bs_total_debt − bs_cash_and_equivalents) / bs_shares_outstanding` converted by the frozen reporting-to-trading rate, now bridges it to the price, as the FCFF baseline already nets debt less cash. A missing bridge input leaves the price missing, and a non-positive implied price is set missing and counted. `study_specification.baselines.classical_valuation` is revised accordingly and the decision is registered in `market_structure.gap_register`. This correction changes the `ev_ebit_baseline` and `ev_ebitda_baseline` figures of the smoke run above. Check: `check_task25_ev_bridge.py`.
12. **The serving declaration and Task 12's reply text (`STUDY_ENVIRONMENT_DECLARATION`, `split_reasoning_task_12`, `make_role_callable_task_12`).** The declaration named vLLM 0.6.6, which predates vLLM's Qwen3 support, and the model `Qwen/Qwen3-4B-Thinking`, which is not a public Hugging Face repository. It now names vLLM 0.19.1 (the newest release with Qwen3 support, Python 3.11 and a CUDA 12.x build) and `Qwen/Qwen3-4B-Thinking-2507`, and `pipeline.serving` pins that checkpoint's commit as reported on 2026-10-23, to be re-verified before a licensed run. A thinking model writes its reasoning before `</think>`; every role reply is now split at the last `</think>`, only the answer is passed on, and the raw text and the reasoning's length stay in the reply record. Check: `check_reasoning_strip.py`.

A separate configuration correction was made in `config.yaml` and `study_config.json`: Task 23 rejects an `early_stopping` key under `baselines.ml.histgbm`, so that key was removed.

**Caveat: the models are not trained or selected on one rule.** Random forest and HistGBM use scikit-learn's default squared-error loss, and the neural network minimises the mean squared error on a standardised target, while MUFASA and the symbolic baselines minimise MAPE, the evaluation metric. The baselines are selected on the validation slice, while MUFASA's incumbent expression is selected on training MAPE, as Algorithm 1 scores candidates on the training data. The paper specifies neither choice, so neither is a deviation, but both bear on how the comparison is read.

### **Verification record**

This example was executed on 2026-10-23 on Windows 11 with Python 3.13.9, NumPy 2.3.5, pandas 2.3.3, SciPy 1.16.3, scikit-learn 1.7.2, statsmodels 0.14.5, matplotlib 3.10.6 and PyYAML 6.0.3. Every run below used `multi_agent_symbolic_discovery_for_financial_fundamental_analysis_draft.ipynb` after all six corrections, unless it is marked otherwise.

- **Notebook executed as stored.** The notebook's 39 code cells, from the first cell through *Task 36: Top-Level Pipeline Orchestrator*, were executed exactly as stored. *Study Assembly* and *Study Execution*, the two cells after Task 36, were not executed.
- **Example executed literally.** The code cells of Steps 1–4 were then executed verbatim, in order, in the same namespace. They were followed by the Step 4.2 smoke cell and the inspection cell. No argument was overridden from outside, and every output shown above is copied from that run.
- **Formatting.** The example cells, concatenated in order, pass `flake8 --max-line-length=99` apart from two kinds of finding. One is undefined names that the notebook defines. The other is warnings created by joining separate cells into one file.
- **Literal smoke run.** Run on seed 11 under the smoke budgets of `make_smoke_configuration`. The driver returned `completed`, and the published status is `pipeline_verified_on_synthetic_data`. All 35 stages are recorded `completed`, no failure ledger was written, and the example cells took 21.9 minutes.
- **Independent repeats.** Two more runs used the same smoke budgets and seed 11, each in its own output directory.
    - The first used calendar-aligned fiscal labels. It completed all 35 stages in 19.0 minutes with the same status.
    - The second set `FISCAL_LABEL_STYLE = "vendor"`, which writes `"FY…"` fiscal labels and adds June filers and a fiscal-year change. This is the case that halted before the quarter-key corrections. It completed all 35 stages in 18.0 minutes with the same status. Every entry of its Task 27 table (`pooled`, `n_scored`, `common_pooled`, `n_common`) equals the calendar-label run's, so the label style no longer changes any score.
- **Targeted checks of the corrections.**
    - *Task 21.* A panel was built with one context present in training and two first seen in the test window. One of the new contexts has its sector in training; the other does not. Before the fix, MUFASA forecast 0 of the 12 held-out rows of the new contexts; after it, all 12. The first new context draws on its sector pool and the second on the market pool. The training context's loss is unchanged, and `test_only_cells` names both new contexts.
    - *Task 27.* Model X covered four rows and model Y two of them. Model X's own-row MAPE is 0.30, and on the two common rows it is 0.10. Model Y's figure is 0.20 on both, with `n_common = 2`. These values match a hand calculation.
    - *Task 29.* In the smoke runs, `table_2_common_support.csv` has one row per market plus the across-market row. Its values match Task 27's `common_pooled` and `n_common`, and the file is listed in Task 29's artefact manifest. `table_2.csv` and the headline `pooled` column are unchanged.
    - *Task 6.* A point-in-time GICS history was built. It records a carrier as Telecommunication Services before 2018-09-28 and as Communication Services after, and a second firm moving from Information Technology to Communication Services on that date. Before the fix, Task 6 halted on the old name. After it, the carrier is *Communications* in 2016 and in 2019, and the second firm is *Technology* in 2016 and *Communications* in 2019.
- **Losses unaffected where nothing changed.** In the smoke runs, the Task 21 change affects no row, because every test-window context of the synthetic panels also occurs in training. The forecast losses of every model are therefore identical to those of a run made before the Task 21 and Task 27 corrections.
- **Not executed.** The Step 4.1 call at `config.yaml` scale was not run, nor was any licensed run. That call has five seeds and full budgets. No figure in this document is a result of the study.

### **Summary of the Execution Flow**

1. **Notebook namespace.** Execute the code cells of `multi_agent_symbolic_discovery_for_financial_fundamental_analysis_draft.ipynb` from *Import Essential Modules* through *Task 36: Top-Level Pipeline Orchestrator*, and append the example cells below them. Nothing is imported from a `.py` folder.
2. **Raw panels.** A seeded `PCG64` process (Faker's role) generates the five panels `run_task_36` requires: 5,760 firm-quarters with valid identifiers, TTM sums, the balance-sheet identity, structural zeros and a forward market-capitalisation target, plus macro, index, membership and GICS-history panels. Every date is `datetime64[ns]` and every fiscal label is calendar-aligned.
3. **Configuration.** `load_study_configuration` reads `config.yaml` into `config`, requires the twelve operational blocks and refuses a stored `environment`. `conform_panels_to_schema` imposes the declared 79-column order and dtypes and checks that the macro series and markets are covered.
4. **Arguments.** `prepare_run_inputs` reads the five seeds `[11, 23, 41, 67, 101]`, measures provenance, composes Task 1's environment, builds the registry `{1: run_task_1, …, 35: run_task_35}` and selects the declared stand-in services for `data_mode="synthetic"`.
5. **Interface call.** `execute_study` calls `run_task_36(config, panels, output_dir, registry=…, seeds=…, services=…, skip=(), data_mode="synthetic", resume=True)`. The driver validates everything first, orders the 35 stages by dependency, runs driver stages 1–4 and 22–35 (Task 22 running stages 5–12, 15, 20 and 21 per seed), checkpoints, writes the manifest and decides the status.
6. **Outcome handling.** A `not_completed` run raises `Task36NotCompletedError` after its manifest and failure ledger are written; `execute_study` returns the attached `.result`, so every stage record remains inspectable.
7. **Assets.** `summarise_study_result` tabulates the stage records, maps (status, data mode) to the published status and extracts, from `outputs[22]["runs"][seed]`, the fitted closed-form equations, the context-indexed weight matrix and the seven-family reliability profiles. Task 27's table and Task 29's `table_2_common_support.csv` compare every model on the same rows.
8. **Scale.** The `config.yaml` call (Step 4.1) is the study run and takes days. The smoke call (Step 4.2) shrinks only search and training budgets and runs a single seed, and its output verifies wiring, never results.
9. **Honesty of status.** Synthetic panels can at best earn `pipeline_verified_on_synthetic_data`. `study_complete` requires the licensed extract (`data_mode="licensed"`), and the operator's served model and services. Fiscal labels of any style are accepted, because every stage keys quarters on the calendar quarter.

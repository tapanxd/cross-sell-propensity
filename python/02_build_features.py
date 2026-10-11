"""
Phase 4 (pandas mirror of Power Query).

Rebuilds the exact same table as powerquery/train_cleaned.m, so the pipeline can run
end to end without Power BI Desktop, and so the two tools can be cross-checked.

Input : data/cross_sell.db (table train_cleaned, built by sql/02_clean.sql)
        data/reference/region_map.csv, data/reference/channel_map.csv
Output: data/processed/engineered_pandas.csv
Check : if data/processed/engineered.csv (the Power BI export) exists, compare cell by cell.
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "cross_sell.db"
REF = ROOT / "data" / "reference"
OUT = ROOT / "data" / "processed" / "engineered_pandas.csv"
PBI_EXPORT = ROOT / "data" / "processed" / "engineered.csv"

# Same top-10 list as the Channel Group step in Power Query (92% of customers)
TOP_CHANNELS = [152, 26, 124, 160, 156, 122, 157, 154, 151, 163]

# 1. Load the cleaned base table and the two reference tables
with sqlite3.connect(DB) as con:
    base = pd.read_sql("SELECT * FROM train_cleaned", con)
region = pd.read_csv(REF / "region_map.csv")
channel = pd.read_csv(REF / "channel_map.csv")
n_base = len(base)
print(f"train_cleaned rows: {n_base:,}")

# 2. Left joins. validate='many_to_one' makes pandas raise if a reference table has a duplicate
#    key -- that is the fan-out bug that would otherwise silently add rows.
df = base.merge(region, how="left", left_on="Region_Code", right_on="region_code",
                validate="many_to_one").drop(columns="region_code")
df = df.merge(channel, how="left", left_on="Policy_Sales_Channel", right_on="channel_code",
              validate="many_to_one").drop(columns="channel_code")

# No-row-loss check: a left join can never have fewer rows, and validate() rules out more
assert len(df) == n_base, f"row count changed: {n_base} -> {len(df)}"
# Orphan check: a null name means a code missing from the reference table
assert df["region_name"].notna().all(), "region code missing from region_map"
assert df["channel_name"].notna().all(), "channel code missing from channel_map"
print(f"after merges:       {len(df):,}  (no row loss, no orphans)")

# 3. Tenure Band -- same rules, same order as the Conditional Column (first match wins)
df["Tenure Band"] = np.select(
    [df["Vintage"] < 90, df["Vintage"] < 180],
    ["new", "established"],
    default="long-standing",
)

# 4. Premium Band -- the 2,630 floor is checked first so it never falls into "low"
df["Premium Band"] = np.select(
    [df["Annual_Premium"] == 2630, df["Annual_Premium"] < 30000, df["Annual_Premium"] < 38000],
    ["base", "low", "medium"],
    default="high",
)

# 5. Channel Group -- top 10 codes keep their name, everything else is "Other"
df["Channel Group"] = np.where(df["Policy_Sales_Channel"].isin(TOP_CHANNELS), df["channel_name"], "Other")

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"wrote {OUT.relative_to(ROOT)}  ({len(df):,} rows, {df.shape[1]} columns)")

# 6. Cross-check against the Power BI export, if present
if PBI_EXPORT.exists():
    pbi = pd.read_csv(PBI_EXPORT)
    # Same columns, same rows (by id), in the same order
    assert list(pbi.columns) == list(df.columns), f"column mismatch:\n{pbi.columns}\n{df.columns}"
    a = df.sort_values("id").reset_index(drop=True)
    b = pbi.sort_values("id").reset_index(drop=True)
    assert len(a) == len(b), f"row count mismatch: pandas {len(a)} vs Power BI {len(b)}"
    mismatches = {c: int((a[c] != b[c]).sum()) for c in a.columns}
    bad = {c: n for c, n in mismatches.items() if n}
    if bad:
        raise SystemExit(f"MISMATCH between pandas and Power Query: {bad}")
    print("cross-check: pandas output matches the Power Query export cell for cell")

    # Band sizes, for the log
    for col in ["Tenure Band", "Premium Band", "Channel Group"]:
        print(f"\n{col}:\n" + (df[col].value_counts(normalize=True) * 100).round(1).to_string())

# Decisions log

One line each: what was chosen and why. Earlier decisions (Phases 1–3, made by hand) are in `docs/00_learning_log.md`; this file starts at the switch to builder mode.

- Kept the existing `region_map` / `channel_map` instead of the `dim_region` / `dim_channel` spec in CLAUDE.md (branch_count, cost tier, deliberate imperfections) — they are already built, verified (0 orphans) and baked into the .pbix; regenerating them would break finished work.
- Power Query M in `powerquery/` is reconstructed from the steps built in Power BI Desktop, because the .pbix stores M compressed inside `DataModel` and it can't be extracted. It is verified by rebuilding the same transforms in pandas and diffing against the Desktop export (`engineered.csv`).
- Used the global Python 3.13 install (pandas 2.3, scikit-learn 1.6, matplotlib 3.10) because no `.venv` exists; pinned those versions in `requirements.txt` so the results reproduce.
- Left `sql/03_buckets.sql` as written. Note: its `WHERE Annual_Premium > 2630` line is commented out, so it reproduces the *unfiltered* cuts (26K/32K/36K). The cuts actually used (30K/38K) came from the filtered version.
- Features in the model: Previously_Insured, Vehicle_Damage, Vehicle_Age, Age, Gender, Driving_License, Annual_Premium, region_name, Channel Group. Left out: Vintage/Tenure Band (flat 12% in EDA), zone/area_type (deterministic relabel of region), channel_type (tail types were round-robin, so noise), Premium Band (raw premium used), id, and Response (the label).
- Logistic regression gets 10-year Age bands (the yes-rate is a hump in age, which a straight line can't fit); the tree model gets raw Age. Premium is log-transformed and scaled for LR (2.6K-540K, skewed).
- All preprocessing sits inside a scikit-learn Pipeline, so encoders and scalers are fitted on training folds only (no test-set leakage).
- Model choice: compared by 5-fold CV ROC-AUC on train only (LR 0.8520, gradient boosting 0.8566). Kept logistic regression because the tree's gain (+0.0046) is too small to give up explainable coefficients. This tolerance rule (tree only if > +0.01) was set after seeing the gap, not before; both models are reported in `reports/metrics.json`.
- class_weight='balanced' for the imbalance, then isotonic calibration so exported probabilities are real yes-rates (needed for "expected responders" in the dashboard). Calibration doesn't change the ranking.
- Tiers: thresholds from train-set score quantiles. High = top 20% (prob >= 0.297), Medium = next 30% (>= 0.037), Low = bottom 50%. On test, Low holds 1.3% of all yes.
- Every customer is scored, with a `split` column so the dashboard computes validation measures on test rows only.
- `customer_scores.csv` is gitignored like the other processed CSVs; the script regenerates it in about 1 minute. Small outputs (`reports/`) are committed.
- Power BI model: `train_cleaned` and `customer_scores` as two tables joined 1:1 on id (both directions) rather than merged, because the scores come from a separate system and refresh on their own. Region/channel stay flattened into `train_cleaned` (from Phase 3); `region_map`/`channel_map` load is disabled to avoid unconnected tables.
- All dashboard numbers are measures; calculated columns only for sort keys (tier, Vehicle_Age, Premium Band).
- Validation measures (rates, lift, captured share) filter to `split = "test"`; lift baseline removes only the tier filter, so lift is "this tier vs calling this slice at random".
- "Expected Responders" = sum of calibrated probabilities, labelled as a model estimate under the original campaign's conditions, not revenue.
- Time intelligence is included as optional only: it needs an assumed snapshot date (2024-12-31) to turn Vintage into a join date, and tenure has no predictive signal.
- Dashboard leaves off Tenure, Premium Band, Gender and the model plots: they don't change who gets called.
- Every measure's expected value is computed independently in pandas (`python/04_dax_check_values.py`) so the Power BI build can be checked number by number.

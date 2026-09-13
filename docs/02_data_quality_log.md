# Phase 2 — Data Quality Log

## Import
- First CSV import: every column came in as TEXT.
- Re-imported with header row: types inferred. Region_Code and Policy_Sales_Channel came in as REAL (e.g. `28.0`) — they are codes, not numbers.
- Annual_Premium is in INR. Not converted.

## Profiling (sql/01_profile.sql)
- Rows: 381,109. Unique ids: 381,109. Duplicates: 0.
- Nulls / empty strings: 0 in every column.
- Age: 20–85. OK.
- Vintage: 10–299 days. Everyone is under 1 year — tenure bands must fit this range; time intelligence will be limited.
- Annual_Premium: 2,630–540,165.
  - 64,877 rows (17%) are exactly 2,630 → a base-plan price, not an error. Keep. Premium bands should not cut inside this spike.
  - 778 rows (0.2%) above 100,000. Keep. "High" band will absorb them. Scale before logistic regression.
- Flags (Driving_License, Previously_Insured, Response): only 0/1. OK.
- Gender: Female 175,020 / Male 206,089. Clean.
- Vehicle_Age: < 1 Year 164,786 / 1-2 Year 200,316 / > 2 Years 16,007. Clean but ordinal — sort order must be set by hand later. "> 2 Years" is small (4%).
- Vehicle_Damage: No 188,696 / Yes 192,413. Almost exactly 50/50 — looks engineered.
- Policy_Sales_Channel: 155 codes. Top 3 = 76% of rows, top 10 = 92%. Long tail of tiny channels. Plan: name the top ~10, group the rest as "Other".
- Region_Code: 53 codes (0–52). Region 28 = 28% alone, top 10 = 64%. Smallest region has 183 rows. No grouping needed. Remember region 28 dominates.
- Response = 1: 12.26% (~46.7K). Heavy imbalance → stratified split, precision/recall/AUC instead of accuracy.

## Cleaning (sql/02_clean.sql)
- Checked Region_Code and Policy_Sales_Channel have no fractional values → cast to INTEGER. They are join keys, so the reference tables must use INTEGER too.
- Raw `train` left untouched. Cleaned copy is `train_cleaned` with explicit types, `id` as PRIMARY KEY, NOT NULL everywhere.
- Nothing removed. No duplicates, nulls, or invalid values to fix.
- Script drops and recreates the table, ends with a row-count check: 381,109 in, 381,109 out.
- No joins or new columns — that's Phase 3.

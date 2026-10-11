# Phases 1–3 — data, reference tables, SQL (done by hand)

You did these phases yourself. The full reasoning is in `docs/00_learning_log.md`. Short version:

- **1 Data.** Kaggle `train.csv`, 381,109 customers who hold a health policy and were offered vehicle insurance. `Response` = accepted (12.26%). Kaggle's `test.csv` has no `Response`, so it isn't used. The test set is cut out of `train.csv`.
- **2 Reference tables.** `region_map` (53 codes → GTA area, zone, urban/suburban/rural) and `channel_map` (155 codes → name, type). They're synthetic, and nothing in them comes from `Response`. → `docs/03_reference_tables.md`
- **3 SQL.** Profiled first, then cleaned. No duplicates, no nulls, no invalid ranges. Region and channel codes were stored as `28.0` and got cast to INTEGER. The 2,630 premium floor (17%) and the 778 premiums over 100K were kept. The raw table is left untouched and `train_cleaned` is built from it. → `sql/`, `docs/02_data_quality_log.md`

**Check it yourself:** in DB Browser, `SELECT COUNT(*), COUNT(DISTINCT id) FROM train_cleaned;` → 381109, 381109.

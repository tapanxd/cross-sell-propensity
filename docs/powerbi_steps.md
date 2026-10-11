# Power BI Desktop — assembly checklist (Phase 6)

Do these in order in `data/processed/cross_sell.pbix`. Each step lists the file with the details and a number to check. Total time is roughly 1–2 hours.

**Before you start:** run `python python/03_train_score.py` (≈1 min) so `data/processed/customer_scores.csv` exists, then `python python/04_dax_check_values.py` to refresh `reports/dax_check_values.md`.

## A. Data (Power Query)
1. Home → **Transform data**.
2. Right-click `region_map` → untick **Enable load**. Same for `channel_map`. (They still feed the merge; they just aren't loaded as separate tables.)
3. Home → New source → **Blank query** → Advanced Editor → paste `powerquery/customer_scores.m` → Done → rename the query `customer_scores`. Fix the file path if needed.
4. Check: `customer_scores` Column profile on `id` (entire data set) → Count = Distinct = 381,109.
5. **Close & Apply**.

## B. Model (`dax/model.md`)
6. Model view: drag `train_cleaned[id]` onto `customer_scores[id]`. In the dialog: Cardinality **One to one (1:1)**, Cross filter **Both**, Make active. *Check: if it suggests Many to one, stop. The `id` types or uniqueness don't match.*
7. Set **Don't summarize** on the columns listed in `dax/model.md`. Hide `customer_scores[id]`.
8. Create the `Geography` (zone → region_name) and `Channel` (channel_type → Channel Group) hierarchies.

## C. Calculated columns and measures (`dax/measures.md`)
9. Add the 3 sort-key columns and set **Sort by column** for `tier`, `Vehicle_Age`, `Premium Band`.
10. Home → Enter data → table `_Measures` → Load. Add the measures in the order listed, then delete `Column1`.
11. Apply the formats in §3 Formatting.
12. **Verify:** new page → Table visual with `tier` + `Customers`, `Share of Customers`, `Test Response Rate`, `Baseline Response Rate`, `Lift vs Random`, `Share of Responders Captured`, `Avg Propensity (Test)`. Compare to `reports/dax_check_values.md`: every number should match to the decimal. Then swap `tier` for `zone`, add `High Tier Lift` and `Expected Responders (High)`, and compare to the zone table. Delete the check page afterwards (or keep it hidden as a "QA" page).

## D. Report pages (`dax/dashboard_spec.md`)
13. Build Page 1 (Who to call), Page 2 (Where the opportunity is), Page 3 (Call list, a drill-through page), Page 4 (Why these customers).
14. View → **Sync slicers**: the Page 1 slicers on pages 1, 2 and 4.
15. Test the drill-down: in the Page 2 matrix, expand Toronto to regions. Test the drill-through: right-click "Mississauga - Central" → Drill through → Call list → table filtered to that region, sorted by rank.
16. Save. Close Power BI before committing so the .pbix isn't mid-write.

## If something looks wrong
| Symptom | Likely cause |
|---|---|
| Every tier shows 381,109 customers | relationship missing or set to single direction from `train_cleaned` |
| Tiers sorted High, Low, Medium | Sort by column not set on `tier` |
| Lift vs Random = 1.00 on every tier row | `Baseline Response Rate` is missing the `REMOVEFILTERS`, or `Test Response Rate` was used in both places |
| Response Rate shows 0 or 1 | it was created as a calculated column, not a measure |
| `probability` reads as 173678 | CSV parsed with a comma-decimal locale; keep the `"en-US"` argument in `customer_scores.m` |

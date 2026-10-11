# Phase 6 — Power BI model, DAX and dashboard

## What was done
- `dax/model.md`: two customer-level tables joined **1:1 on `id`**: `train_cleaned` (attributes, from Power Query) and `customer_scores` (model output, from Python). A `_Measures` table holds every number.
- `dax/measures.md`: 3 sort-key columns, 17 measures (counts, rates, lift vs random, shares, expected responders), plus optional time intelligence.
- `dax/dashboard_spec.md`: 4 pages. Who to call (headline) → Where the opportunity is (drill-down) → Call list (drill-through) → Why these customers (drivers + model check).
- `docs/powerbi_steps.md`: the click-by-click build in Power BI Desktop. You have to do this part by hand.
- `python/04_dax_check_values.py` → `reports/dax_check_values.md`: the number every measure should show, worked out independently in pandas.

## Why this way
- **Measures, not columns, for anything that's a number on a visual.** A measure is recalculated for whatever is filtered (a tier, a zone, a slicer). A column is fixed per row at refresh. Columns are used only for sort keys.
- **Validation measures use the test set only.** The model saw the train rows, so lift measured on them would be flattering. The `split` column from Python makes that filter one line of DAX.
- **Lift is relative to the slice, not the whole company.** Calling Peel's High tier should be compared with calling Peel at random. `REMOVEFILTERS(customer_scores[tier])` does exactly that: it drops the tier, keeps the region. That's why High-tier lift is 3.6x in Peel and 2.4x in Toronto.
- **Two tables instead of one:** the scores come from a different system and get refreshed separately. In a real team you'd swap the CSV without touching the customer query.
- **What's left off:** Tenure (no signal), Premium/Gender (weak), the technical model plots. The dashboard only shows what changes who gets called.

## Key concept: what CALCULATE changes
A measure always runs inside a **filter context**: the set of filters from the visual's row, the slicers and the page. `CALCULATE(expression, filter…)` runs the expression in a *modified* filter context.
- `CALCULATE([Customers], customer_scores[split] = "test")` **adds** a filter. It keeps the tier/zone and also restricts to test customers.
- `CALCULATE([Test Response Rate], REMOVEFILTERS(customer_scores[tier]))` **removes** one filter and keeps the rest.
- `CALCULATE([Lift vs Random], customer_scores[tier] = "High")` **replaces** the tier filter with High, whatever row it's on.
The filter is applied to `customer_scores`. The 1:1 relationship then carries it to `train_cleaned`, where rows are counted. That's why the relationship has to filter in both directions.

## Headline numbers the dashboard will show (test set)
- High tier: 76,828 customers (20%), 34.6% yes-rate, **2.82x** random, holds 57% of all yeses.
- Low tier: half of all customers, 0.3% yes-rate.
- Toronto holds 72% of the High tier. Web / Aggregator (35% of customers) has none.

## Check it yourself
Build the QA table from step 12 in `docs/powerbi_steps.md` and compare it to `reports/dax_check_values.md`. If a number is off, the "If something looks wrong" table at the end of the steps file names the usual cause.

# Learning log / interview notes

Running list of what I learned and the judgement calls I made. Plain words. Add to it every phase.

## Big picture
- This is a data analytics project with a light predictive layer. The model is one step in the pipeline; the ranked list and the dashboard are the product.
- Descriptive = "who said yes/no in the past". Predictive = "how likely is each customer to say yes". The VP needs the second one — a call list.
- Output of the whole thing: customer id + probability + tier (high/med/low).
- The model says "more or less likely", never "will / won't". Don't use "will" with stakeholders.
- No invented dollar or % impact. Success = beats random targeting on a held-out set. Validate with real data later — say that as a limitation.

## Phase 1 — framing
- Health policy = the product they already have. Vehicle insurance = the second product.
- `Response` is the record of a past campaign. It's the label, not a cheat sheet. Carry it through SQL and Power Query untouched; never build a feature from it; use it only as the training label in Python and for validation on the dashboard.
- Kaggle's `test.csv` has no `Response`, so it's useless here. My test set is carved out of `train.csv`.
- Train/test split: train on one pile, check on a pile the model never saw. Without it the model just memorises and looks better than it is.
- Stratified split: keep the ~12% yes-rate the same in both piles so the evaluation isn't skewed by chance.
- Why not accuracy: 88% say no, so "predict no for everyone" is 88% accurate and useless. Use precision / recall / ROC-AUC.

## Phase 2 — SQL
- Diagnose before you treat. Profile and write down counts first, decide fixes after.
- First CSV import made everything TEXT. `MAX()` on text compares as strings ('9' > '10'). Type matters before you profile ranges.
- Region and channel codes came in as REAL (28.0). They are codes, not quantities. Verified no fractional values, then cast to INTEGER. INTEGER vs TEXT is a judgement call — INTEGER sorts naturally and joins cleanly, but Power BI will try to sum it, so set "Don't summarize" later. Whatever you pick, join keys must match on both sides.
- A value repeated 64,877 times (17% at exactly 2,630) is not an error. Errors are scattered; one repeated value is a rule in the source system — a floor / base-plan price. Keep it, treat it as its own band later. Don't speculate about *why* in an interview; say "I'd confirm with the product team."
- 778 rows (0.2%) above 100K premium: keep, no flag column. Phase 2 has no engineered columns — a flag column would be one.
- Vintage max is 299 days: everyone is under a year. Tenure bands must live inside that. Time intelligence will be limited.
- 155 channels, top 3 = 76%, top 10 = 92%. 53 regions, more evenly spread, smallest still 183 rows. Channels need grouping; regions don't.
- Vehicle_Age is ordinal (< 1, 1-2, > 2) — tools won't know the order, set it by hand later.
- Window functions: `SUM() OVER()` for a total without a second query. Cumulative with `ORDER BY` defaults to RANGE, which lumps ties together — use `ROWS UNBOUNDED PRECEDING` plus a tiebreaker. Round last, never sum rounded numbers.
- Keep raw table untouched; build `train_cleaned` from it. `CREATE TABLE AS SELECT` can't declare a primary key, so use explicit DDL + `INSERT ... SELECT`. Constraints (PRIMARY KEY, NOT NULL) enforce what profiling found instead of just recording it.
- Scripts must be re-runnable (`DROP TABLE IF EXISTS`) and end with a row-count check.
- Comment the decisions, not the syntax. Don't write comments you wouldn't say out loud.
- The .db file is a build artefact — don't commit it. Commit the SQL scripts and the log.

## Reference tables
- Why they exist: (1) the multi-table join is the skill being tested, (2) codes mean nothing to a stakeholder — "Region 28" vs "Toronto Downtown Core".
- Think "what would I ask IT for", not "what columns can I invent". 2–4 columns each.
- Zone (Toronto/Peel/York/Durham/Halton) and area_type (urban/suburban/rural) are two independent roll-ups of the same 53 regions — that's a hierarchy for drill-down.
- Channel type has 6 values. Only the top 10 codes (92% of rows) got deliberate assignment; the tail was mechanical and will show as "Other".
- Nothing in a reference table may be derived from `Response` — that's leakage.
- Orphan check before joining: left join, count nulls on the reference side, must be 0.

## Phase 3 — Power Query (in progress)
- SQLite via ODBC hands every number over as Decimal, ignoring the INTEGER declarations. Set types explicitly in a Changed Type step, one step per query. Don't forget `id`.
- Power Query is a recorded list of steps (Applied Steps). The UI and the M in the formula bar are the same thing; edit either.
- Base table = the one whose rows you refuse to lose = `train_cleaned`.
- Left outer join: keep every customer, attach reference data if it exists. Inner would drop customers with an unknown code; right/full would add regions with no customers. Today inner and left give the same result (0 orphans) — the reason to choose left is what happens the day a new code appears upstream.
- Proof of no row loss: merged count must equal base count exactly. Fewer = wrong join kind. More = fan-out (duplicate key in the reference table). Check count AND distinct on `id` on the entire data set, not the 1000-row preview.
- Merges can reorder rows. Never rely on row order after one.
- Turn off "use original column name as prefix" when expanding, or fix the names list in the M.
- Conditional Column has no "between" — rules run top to bottom, first match wins, so order them monotonically. Be deliberate about `>` vs `>=` at the boundary and keep the same convention everywhere.
- Two ways to justify a band: (A) business-meaning cuts (90 days, 180 days) or (B) distribution cuts (terciles, natural breaks). Vintage is uniform → no natural break → use A. Premium is very skewed with a 17% spike → use B, with the spike as its own "base" band so no cut lands inside it.
- Tenure Band: < 90 new, < 180 established, else long-standing. Checked Vintage distribution first: 290 distinct values, flat — so cuts are business-meaning (first quarter / half year), not statistical.
- `NTILE(n)` = sort and deal rows into n equal piles; the max value in pile 1 is the first cut. `MAX(CASE WHEN bucket = 1 THEN x END)` is just "max of x, filtered to pile 1".
- Premium terciles must be computed on the NON-base rows (`WHERE > 2630`), because the band rules check `= 2630` first, so the tercile rules only ever see non-base rows. Computing on all rows gave different (lower) cuts — wrong population.
- Premium Band: = 2630 base, < 30K low, < 38K medium, else high. Cuts rounded from 30,282 / 38,365 so a stakeholder can remember them. Result: base 17%, low 26%, medium 27%, high 28%. Four bands, not three — folding base into low would make low 45%.
- Real world: (1) use the business's existing plan tiers if they exist, (2) otherwise propose rounded cuts and get stakeholder sign-off, (3) pure percentiles only for internal work. A floor/default value is almost always its own tier. Bands are for reporting; a model can take the raw number.
- Each Power Query step is a function of the previous step's output — `#"Expanded channel_map"` in a step's M is just the name of the step above. Delete a middle step and the next one breaks.
- Custom Column comes out typed `any` (ABC123). Set the type right after, or profiling won't run and the data model gets an untyped column.
- The query icon turning to `ABC` means the query returns a text value, not a table — a bad step. Find it in Applied Steps and delete it.
- Query Settings / Applied Steps pane: View tab → Query Settings if hidden.
- Grouped channel: `channel_type` (6 kinds, from the merge) answers "which kind of channel works". A separate `Channel Group` (top-10 codes by name + "Other") answers "which specific channels matter" — different question, worth both. "Is one of" in M is `List.Contains`.

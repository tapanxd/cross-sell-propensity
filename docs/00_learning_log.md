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

## Phase 3 wrap-up (from the Definition of Done)
- Join type, full answer: left outer keeps every customer. Inner would give the same 381,109 today because there are 0 orphans. But the day a new code shows up upstream, inner silently drops those customers and left keeps them with a blank. A duplicate code in a reference table would show up as MORE than 381,109 rows (fan-out), which is why I checked distinct id = count and not just the count.
- Four premium bands: the 2,630 floor is 17% of customers. Folding it into "low" would make low 45%, and any tercile cut taken over all rows lands inside the spike.
- Exporting 381K rows out of Power BI: the table visual's "Export data" stops at 30,000 rows. DAX Studio (`EVALUATE 'table'`, output to File) has no limit.
- The newer .pbix format keeps M compressed inside `DataModel`, so it can't be read back out of the file. I keep a copy of each query as a `.m` file in `powerquery/`.
- Cross-check between tools: the same transforms rebuilt in pandas (`python/02_build_features.py`) match the Power Query export on every cell. If two tools agree, a typo in one of them would have shown up.
- `merge(validate="many_to_one")` in pandas is the fan-out check built in. It errors if the right-hand table has a duplicate key.

## Phase 4 — model (Python)
- What the EDA showed (yes-rate by group, overall 12.26%): already insured 0.09% vs 22.6% not. No past vehicle damage 0.5% vs 23.8% with damage. Vehicle age 4% / 17% / 29%. Age is a hump: 20s 4%, 30-49 ~21%, 70+ ~7%. Tenure is flat (12.2 / 12.3 / 12.3), so it has no signal. A flat result is a finding too.
- Low-cardinality categories (3-6 values) are the easiest for a model, not a problem. The problem is 155 values with a handful of rows each.
- You don't have to know in advance whether a feature matters. A useless feature just gets a coefficient near zero. Looking first (EDA) still pays off, because it gives the memo its descriptive findings.
- One-hot encoding turns a text column into one 0/1 column per value. Scaling puts Age (20-85) and Premium (2.6K-540K) on the same footing for logistic regression. Trees don't need either.
- Fit the scaler/encoder on train only. A `Pipeline` guarantees this, because cross-validation refits it on each training fold.
- Stratified split: 304,887 train / 76,222 test, both exactly 12.26% yes.
- Cross-validation = split the training set 5 ways, train on 4, score on 1, rotate. It gives a model-choice score without touching the test set.
- LR 0.852 vs trees 0.857 AUC. I kept LR because 0.005 isn't worth losing explainable coefficients (design.md: interpretability first). Be honest that this rule was set after seeing the gap.
- class_weight='balanced' makes a missed yes cost more during training. Side effect: scores average about 0.5, not 0.12. Calibration (isotonic) maps them back to real rates without changing the order.
- At a 0.5 cut-off: recall 92%, precision 28%. You can't max both. Tiers replace the single cut-off, and the business picks how deep to call.
- Test results: AUC 0.853. Top 20% -> 34.7% yes, 2.8x random, 57% of all yes. Top 50% -> 98.7% of all yes. Bottom 50% (Low tier) -> 0.3% yes-rate.
- Coefficients are "holding everything else equal", so they can disagree with raw group averages (Vehicle_Age 1-2 Year shows negative once age and damage are accounted for).
- Train rows were seen in training, so dashboard validation uses test rows only (`split` column).

## Phase 5 — Power BI model and DAX
- Calculated column = computed once per row at refresh, stored. Measure = computed for whatever is filtered, every time a visual draws. Rates, totals and lift are always measures. "Response rate" as a column would just be 0 or 1 per row.
- Text sorts alphabetically (High, Low, Medium). A numeric sort-key column plus "Sort by column" fixes it. This is a legitimate use of a calculated column.
- Filter context = the filters coming from the visual row, slicers and page. CALCULATE changes it: it can add a filter (split = test), remove one (REMOVEFILTERS tier) or replace one (tier = High).
- Lift vs random, in plain words: the yes-rate of the tier ÷ the yes-rate you'd get calling the same slice at random. The random rate = the same measure with the tier filter removed. Lift is relative to the slice, so High-tier lift is 3.6x in Peel but 2.4x in Toronto, because Toronto's baseline is already higher.
- 1:1 relationship: Power BI forces "Both" directions. It's needed because the tier filter sits in the scores table while the rows being counted sit in the customer table, and vice versa for region.
- Many to one suggested on an id-to-id relationship = a duplicate or mismatched type somewhere. Check before accepting.
- Dashboard design: lead with the decision (who to call), drill down for where, drill through for the actual list, and keep the "why" and the model check for last. Leave off anything that doesn't change the decision: tenure, premium band, model curves.
- Findings the dashboard will show: High tier = 20% of customers, 57% of the yeses, 2.82x random. Toronto has 72% of the High tier. The biggest channel (Web / Aggregator, code 152) has no High-tier customers at all.
- Time intelligence needs a real date. Vintage is days, so a join date needs an assumed snapshot date, which is invented. Fine to practise, but label it as illustrative.
- Check DAX against an independent calculation (pandas) before trusting it.

## Phase 6 — write-up
- Lead with the recommendation, not the process. Four lines: call High, skip Low, extend with Medium, rank hardest outside Toronto.
- Only quote numbers that were measured (test set, raw data). No revenue, no "efficiency". Impact is described as how it would be tested.
- Validation plan = randomised pilot. Call a random half of the High tier and hold the other half back, plus a small random sample of Medium and Low. The only difference between the groups is the call, so the gap in acceptance is the real lift.
- Say the limits before being asked: one public campaign, channel effect vs customer mix can't be separated, labels are synthetic.
- The model mostly runs on two facts (already insured, past damage). That's a finding: a simple "don't call" rule covers half the base even without a model.

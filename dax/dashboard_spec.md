# Dashboard spec

**Audience:** VP of Distribution (Phase 1). **Decision:** who the sales team calls first, and through which channels and regions.
Everything on the pages serves that decision. Built-but-left-off items are listed at the end, with the reason.

Theme: default. One accent colour for "High" across every visual (e.g. dark blue `#2B6CB0`). Rates and shares as %, 1 decimal. Lift as `0.00x`.

---

## Page 1 — Who to call (headline)

**Title text box:** "Call the High tier first: 20% of customers, 57% of the yeses (held-out test set)"

| Position | Visual | Fields | Settings |
|---|---|---|---|
| Top row, 4 cards | Card | `High Tier Customers` | label "Customers to call first" |
| | Card | `Lift vs Random` | visual filter `customer_scores[tier]` = High · label "High tier vs random" → 2.82x |
| | Card | `Share of Responders Captured` | visual filter tier = High · label "Share of yeses in High tier" → 57.2% |
| | Card | `Test Response Rate` | visual filter tier = Low · label "Low tier yes-rate (skip)" → 0.3% |
| Middle left | **Line and clustered column chart** | X: `tier` · Columns: `Test Response Rate` · Line: `Baseline Response Rate` | sorted by Tier Sort; data labels on. Shows each tier's yes-rate against the call-at-random rate |
| Middle right | Clustered bar | Y: `Channel Group` · X: `High Tier Customers` | sort descending. Web / Aggregator, the biggest channel, has **no** High-tier customers |
| Right edge | Slicers | `Geography` hierarchy (dropdown), `Channel Group` (dropdown) | sync slicers to pages 2 and 4 |
| Bottom | Text box | "Rates and lift measured on 76,222 customers held out from training. Region and channel names are illustrative labels for the dataset's codes. Expected values are model estimates, not revenue." | small grey font |

## Page 2 — Where the opportunity is (drill-down)

| Visual | Fields | Settings |
|---|---|---|
| **Matrix** | Rows: `Geography` (zone → region_name) · Values: `Customers`, `High Tier Customers`, `High Tier Share`, `Expected Responders (High)`, `High Tier Lift` | drill-down on (the double-arrow "expand all" icon). Conditional formatting: data bars on `High Tier Customers` |
| Clustered bar | Y: `Channel` hierarchy (channel_type → Channel Group) · X: `High Tier Customers` | drill-down on |
| Clustered column | X: `area_type` · Y: `High Tier Share` | |
| Card | `Expected Responders (High)` | label "Expected yeses if High tier is called (model estimate)" |

What it shows: Toronto holds 55,574 of the 76,828 High-tier customers. But High-tier lift is *higher* outside Toronto (Durham 4.19x, Peel 3.62x vs Toronto 2.41x), because their baseline rate is lower. Ranking matters most where random calling does worst.

## Page 3 — Call list (drill-through)

- Page settings: **Drill through** → add `region_name` and `Channel Group`. "Keep all filters" on.
- From page 2, right-click a region or channel → Drill through → Call list.

| Visual | Fields | Settings |
|---|---|---|
| Table | `rank`, `train_cleaned[id]`, `probability`, `tier`, `Age`, `Vehicle_Age`, `Vehicle_Damage`, `Previously_Insured`, `Channel Group`, `region_name` | visual filter tier in (High, Medium); sort by `rank` ascending; `probability` as % |
| Card | `High Tier Customers` | |
| Card | `Expected Responders (High)` | |

This page is the actual output the sales team uses: a ranked list, filtered to their patch.

## Page 4 — Why these customers (drivers + model check)

| Visual | Fields | Point |
|---|---|---|
| Clustered column | X: `Previously_Insured` · Y: `Response Rate` | already insured → 0.09% |
| Clustered column | X: `Vehicle_Damage` · Y: `Response Rate` | no past damage → 0.5% |
| Clustered column | X: `Vehicle_Age` (sorted) · Y: `Response Rate` | 4% → 17% → 29% |
| Clustered column | X: Age bins (right-click `Age` → New group → Bin, size 10) · Y: `Response Rate` | hump, peak 30–49 |
| Line and clustered column | X: `tier` · Columns: `Test Response Rate` · Line: `Avg Propensity (Test)` | predicted vs actual, near-identical → the probabilities can be trusted |
| Text box | "These patterns are from one historical campaign in the Kaggle dataset. Before acting on a real customer base, run a live A/B test (see summary)." | |

---

## Built, but deliberately left off
- **Tenure Band / Vintage:** flat 12% yes-rate in every band. A slicer for it would invite reading meaning into noise.
- **Premium Band, Gender:** weak differences (10–14%). They'd add visuals without changing who gets called.
- **Model coefficients, ROC/PR curves:** for the technical audience (in `reports/figures/`), not the VP.
- **Time-intelligence measures:** they rely on an assumed snapshot date (see `dax/measures.md` §4).
- **Raw region codes / 155 channel names:** replaced by the hierarchy and Channel Group.

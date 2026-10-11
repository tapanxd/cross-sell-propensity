# Interview notes

The long version, with every step, is `docs/00_learning_log.md`. This is the short list to revise before an interview.

## The 90-second version (say it out loud, time it)
> "The ask was from distribution: most customers hold one policy, and sales can't tell who's worth calling about a second one. I used a public insurance dataset, 381,000 health-policy customers who'd been offered vehicle insurance, 12% accepted, and treated that past campaign as the training history.
>
> I profiled and cleaned it in SQL first. The main finding there was that 17% of premiums sat on one exact value, a base-plan floor rather than bad data, so it got its own band later. In Power Query I joined in region and channel reference tables with a left join and checked there was no row loss or fan-out, then built tenure, premium and channel-group features.
>
> The model is a logistic regression. I picked it over gradient boosting because the trees were only half a point of AUC better, and coefficients are something I can explain to a VP. I judged it on a held-out 20% using AUC and lift, not accuracy, because with 12% positives 'predict no' is 88% accurate and useless.
>
> The result: the top-scored fifth of customers accepted at 2.8 times the random rate and held 57% of all the yeses, while the bottom half, mostly people already insured elsewhere, accepted at 0.3%. So the recommendation is: call the top tier first and stop calling the bottom half. And before acting on it for real, run a controlled pilot, because this is one historical campaign, not our own customers."

## Decisions and why

| Decision | Choice | Why (one line) |
|---|---|---|
| Framing | Health = existing product, vehicle = second product | That's the only cross-sell the dataset's outcome column records |
| Test set | Carved from `train.csv`, stratified 80/20 | Kaggle's `test.csv` has no labels; stratify keeps 12.26% yes in both piles |
| `Response` | Label and validation only, never a feature | Using it to build features is leakage |
| Code types | REAL → INTEGER after checking for 0 fractional values | They're join keys, so both sides must match |
| 2,630 premium (17% of rows) | Kept, own "base" band | One value repeated 65K times is a system rule, not an error |
| Premium > 100K (0.2%) | Kept, no flag | Too few to matter; "high" band absorbs them |
| Raw table | Left untouched; `train_cleaned` built from it | Re-runnable from the source of truth |
| Join type | Left outer from `train_cleaned` | Never lose a customer; inner would silently drop new codes later |
| Row-loss check | Count **and** distinct id = 381,109 | Count alone misses fan-out from a duplicate key |
| Tenure bands | < 90 / < 180 / rest (days) | Vintage is flat, so business cuts (quarter, half-year) beat statistical ones |
| Premium bands | base / < 30K / < 38K / rest | Terciles of the non-base rows, rounded so people remember them |
| Channel Group | Top 10 codes + Other | Top 10 = 92% of customers; nobody wants a 155-option slicer |
| Features dropped | Tenure, zone/area_type, channel_type, Premium Band | No signal / duplicates region / round-robin noise / raw premium used instead |
| Age | 10-year bands for LR | Yes-rate is a hump in age; a straight line can't fit it |
| Model | Logistic regression over gradient boosting | +0.005 AUC isn't worth losing explainability (rule set after seeing the gap) |
| Imbalance | class_weight='balanced' + calibration | Weighting so the rare yes isn't ignored; calibration so probabilities are real rates |
| Metric | ROC-AUC + lift, not accuracy | The output is a ranking; "predict no" is 88% accurate |
| Tiers | Top 20% / next 30% / bottom 50%, cuts from train scores | 20% ≈ one campaign's capacity; bottom 50% is near-zero yes-rate |
| Dashboard numbers | All measures, validation on test rows only | Measures follow the filters; train rows are flattered |
| Lift baseline | Remove only the tier filter | "This tier vs calling this region at random" |
| Two tables in PBI | Customers and scores, 1:1 | Scores come from another system and refresh on their own |

## Questions to expect, and the answer
- **"How would you validate this without real outcome data?"** Run a randomised pilot: call a random half of the High tier and a small random sample of the other tiers, then compare acceptance. That gives real lift. Add premium and call cost to check profitability. Monitor predicted vs actual monthly.
- **"Why not accuracy?"** 88% say no, so a model that says "no" to everyone is 88% accurate and finds nobody. I care about ranking, so AUC, plus lift in the top tiers.
- **"Precision or recall, which matters more here?"** It depends on call cost. Expensive calls favour precision (call only High). Cheap outreach favours recall (High + Medium catches 99% of the yeses). The tiers let the business pick instead of me hard-coding a threshold.
- **"Isn't the model just two variables?"** Mostly, yes: already-insured and past damage do the heavy lifting. That's a finding, not a weakness. It means the "who not to call" rule could run even without a model. The model adds the ranking *within* the remaining half.
- **"Why is the biggest channel useless?"** On this data, web/aggregator customers produce no High-tier scores. I can't tell whether that's the channel or the customers it attracts. That's what the pilot would separate.
- **"What would you do differently?"** Use the business's own plan tiers for premium bands if they existed. Get real campaign costs. Build out-of-fold scores so the train rows aren't scored in-sample.
- **"Why isn't tenure in the model?"** Same 12% yes-rate in every band. Flat is a result too.

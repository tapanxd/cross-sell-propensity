# Phase 5 — Model: rank customers by likelihood of saying yes

## What was done
`python/03_train_score.py`:
1. Split 381,109 customers 80/20 with **stratification**, so both piles have exactly 12.26% yes. The 76,222-row test set is never used for training or for choosing the model.
2. Trained two models, both with `class_weight='balanced'`: **logistic regression** and **gradient boosting** (trees).
3. Compared them with 5-fold cross-validation on the training set: LR 0.852 AUC, trees 0.857.
4. **Kept logistic regression.** The trees win by only 0.005 AUC, and LR can be explained line by line (below).
5. **Calibrated** the scores so "probability" means a real yes-rate.
6. Scored every customer, assigned tiers, and exported `data/processed/customer_scores.csv` (`id, probability, tier, split, rank`).

## Results on the held-out test set (real numbers, not projections)
| | |
|---|---|
| ROC-AUC | **0.853** (0.5 = coin flip) |
| Top 20% by score | 34.7% yes vs 12.3% at random → **2.8× lift**, catches 57% of all yes |
| Top 50% by score | catches **98.7%** of all yes |

| Tier | Share of customers | Actual yes-rate | Share of all yes |
|---|---|---|---|
| High (top 20%) | 20% | 34.6% | 57% |
| Medium (next 30%) | 30% | 17.1% | 42% |
| Low (bottom 50%) | 50% | 0.3% | 1% |

Plots: `reports/figures/`. All numbers: `reports/metrics.json`.

## Why this way
- **Why not accuracy:** 88% of customers say no, so "predict no for everyone" is 88% accurate and finds nobody. **ROC-AUC** measures how well the model *ranks* yes above no, which is what a call list needs. Lift and capture turn that into the VP's question: "if we call the top X%, how much better than random is it?"
- **Precision vs recall:** at the default 0.5 cut-off the balanced model catches 92% of the yes (recall), but only 28% of the people it flags say yes (precision). We don't use 0.5. The tiers *are* the cut-off, and the VP picks the trade-off by choosing which tiers to call.
- **class_weight='balanced':** makes a missed "yes" cost about 7× more than a wrong "no" during training, so the rare class isn't ignored. The side effect is inflated scores (average around 0.5), which is why calibration follows.
- **Calibration (isotonic):** maps scores back to real rates without changing their order. Check: mean predicted 12.29% vs actual 12.26%. High tier predicted 34.7% vs actual 34.6%.
- **Tier cut-offs:** taken from the *training* score distribution. Top 20% = a plausible one-campaign budget. Bottom 50% = the group with a 0.3% yes-rate (mostly already insured or no past damage), so calling them is almost pure waste.
- **Features dropped:** Vintage / Tenure Band (flat 12% in every band, no signal). zone / area_type (just region relabelled). channel_type (the tail channels' types were assigned round-robin, so it's noise). Premium Band (the model gets the raw premium).
- **Age as bands for LR:** the yes-rate rises and then falls with age (a hump). A straight-line model can't bend, so it gets 10-year bands.

## Key concept: reading the coefficients
Each bar in `reports/figures/logreg_coefficients.png` shows how a feature pushes the odds of "yes" **while everything else is held equal**. Previously_Insured (−4.0) is by far the strongest "no". Vehicle_Damage = Yes (+2.0) is the strongest "yes". Because they're "holding everything else equal", a coefficient can disagree with a simple group average. Example: Vehicle_Age "1-2 Year" shows negative here, even though its raw yes-rate is high. That's because the effect is already explained by age and damage.

## Honest limits
- `Response` comes from the Kaggle dataset, not a real company's campaign. These are real results *on that data*. Whether they hold for a real book of customers needs a live test (see `docs/summary.md`).
- Region and channel names are synthetic labels. "Outbound Call Centre has low response" really means "channel code 160 has low response".
- Train-split customers were seen during training, so their scores are slightly optimistic. Any validation (lift, actual-vs-predicted) uses `split = "test"` only.

## Check it yourself
- `python python/03_train_score.py` (about 1 min) prints CV AUCs, the tier table and the gains.
- Open `customer_scores.csv` and filter `split = test`, `tier = High`. Average the matching `Response` from `engineered.csv`: it should be about 0.346.

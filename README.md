# Cross-Sell Propensity & Opportunity Sizing

Which existing health-insurance customers are the best candidates for a second product (vehicle insurance), and how should a sales team prioritise outreach when time is limited?

An end-to-end analytics project: SQL → Power Query → Python → Power BI → business memo. Every judgement call is documented in `docs/`.

**Result (held-out test set, 76,222 customers):** ROC-AUC 0.853. The top-scored 20% of customers accepted at 34.6% vs 12.3% at random (**2.8× lift**) and held 57% of all acceptances. The bottom 50% accepted at 0.3%. → [`docs/summary.md`](docs/summary.md)

## Data
- **Kaggle: Health Insurance Cross Sell Prediction** (`train.csv`, 381,109 rows). Customers who hold a health policy and were offered vehicle insurance; `Response` = accepted (12.26%).
- **Synthetic reference tables** (`data/reference/`): `region_map` (53 region codes → GTA area, zone, urban/suburban/rural) and `channel_map` (155 channel codes → name, type). Stand-ins for the lookup tables a real analyst would request. Nothing in them is derived from `Response`.
- `Annual_Premium` is in INR, not converted.

## Pipeline
| # | Phase | Tool | Output | Explainer |
|---|---|---|---|---|
| 1 | Data | Kaggle | `data/raw/train.csv` | [phase 1–3](docs/explain/phase_1-3_foundation.md) |
| 2 | Reference tables | — | `data/reference/*.csv` | [03_reference_tables](docs/03_reference_tables.md) |
| 3 | Profile + clean | SQLite | `sql/`, `train_cleaned` | [02_data_quality_log](docs/02_data_quality_log.md) |
| 4 | Joins + features | Power Query (+ pandas mirror) | `powerquery/*.m`, `engineered.csv` | [phase 4](docs/explain/phase_4_power_query.md) |
| 5 | Model | Python / scikit-learn | `customer_scores.csv`, `reports/` | [phase 5](docs/explain/phase_5_model.md) |
| 6 | Data model + DAX + dashboard | Power BI | `dax/`, `.pbix` | [phase 6](docs/explain/phase_6_powerbi.md) |
| 7 | Write-up | — | `docs/summary.md`, `docs/interview_notes.md` | [phase 7](docs/explain/phase_7_writeup.md) |

Status: [`PROGRESS.md`](PROGRESS.md). Decisions: [`docs/decisions.md`](docs/decisions.md).

## Run order
Requires Python 3.13 with `pip install -r requirements.txt`, DB Browser for SQLite, Power BI Desktop, the 64-bit SQLite ODBC driver and DAX Studio.

1. Download `train.csv` from Kaggle into `data/raw/` (gitignored).
2. In DB Browser, create `data/cross_sell.db`. Import `train.csv` as table `train`, and `data/reference/region_map.csv` / `channel_map.csv` as `region_map` / `channel_map`.
3. Run `sql/01_profile.sql` (diagnostics only), then `sql/02_clean.sql` (creates `train_cleaned`, ends with a row-count check).
4. Create an ODBC DSN `cross_sell` → `data/cross_sell.db`. Open `data/processed/cross_sell.pbix` and Refresh (steps: [`docs/powerquery_steps.md`](docs/powerquery_steps.md)).
5. Export the engineered table: DAX Studio → `EVALUATE 'train_cleaned'` → output File → `data/processed/engineered.csv`.
6. `python python/02_build_features.py`: rebuilds the same table in pandas and checks it matches the Power BI export. (If you skip steps 4–5, the model falls back to this pandas output.)
7. `python python/01_train_score.py`: EDA, yes-rate by group.
8. `python python/03_train_score.py`: trains, evaluates, writes `customer_scores.csv`, `reports/metrics.json` and `reports/figures/` (about 1 min).
9. `python python/04_dax_check_values.py`: expected value for every DAX measure → `reports/dax_check_values.md`.
10. In Power BI, follow [`docs/powerbi_steps.md`](docs/powerbi_steps.md): load the scores, build the relationship, measures and the 4 dashboard pages.

## Repo layout
```
data/raw/          Kaggle CSV (gitignored)
data/reference/    synthetic region/channel tables
data/processed/    .pbix; engineered + scored CSVs (gitignored, regenerated)
sql/               profiling and cleaning scripts
powerquery/        M for every Power Query query
python/            EDA, pandas mirror, model, DAX check values
dax/               measures, model diagram, dashboard spec
reports/           metrics.json, coefficients, figures, DAX check values
docs/              problem statement, data-quality log, decisions, explainers, summary, interview notes
```

## Constraint and limitations
There is no real customer base behind this. No dollar or efficiency figures are claimed. Model results (AUC, lift) are real **on the Kaggle data**. `Response` comes from that public dataset, not from a company's own campaign history, so the validation plan in `docs/summary.md` (a randomised pilot) is the step before acting on it. Region and channel names are illustrative labels for the dataset's codes.

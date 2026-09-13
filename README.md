# Cross-Sell Propensity & Opportunity Sizing

Which existing health-insurance customers are the best candidates for a second product (vehicle insurance), and how should a sales team prioritise outreach when time is limited?

An end-to-end analytics project: SQL → Power Query → Python → Power BI → business memo. Built as a learning exercise in Power BI / DAX and business framing; every judgement call is documented in `docs/`.

## Data

- **Kaggle — Health Insurance Cross Sell Prediction** (`train.csv`, 381,109 rows). Customers who hold a health policy and were pitched vehicle insurance; `Response` records whether they accepted (~12%).
- **Synthetic reference tables** (`data/reference/`): `region_map` (53 region codes → GTA municipality, zone, urban/suburban/rural) and `channel_map` (155 channel codes → name, channel type). These stand in for the lookup tables a real analyst would request from other systems. Nothing in them is derived from `Response`.

`Annual_Premium` is in INR and is not converted.

## Pipeline

| Phase | Tool | What happens | Where |
|---|---|---|---|
| 1 | — | Frame the business question | `docs/01_problem_statement.md` |
| 2 | SQLite | Profile, then clean. Types corrected, nothing removed. | `sql/`, `docs/02_data_quality_log.md` |
| 3 | Power Query | Left-join reference tables; add Tenure Band, Premium Band, Channel Group | `data/processed/cross_sell.pbix` |
| 4 | Python | Stratified split, logistic regression baseline, score + tier every customer | `python/` (in progress) |
| 5 | Power BI | Data model, DAX measures (tier counts, lift vs random), dashboard | `cross_sell.pbix` (in progress) |
| 6 | — | One-page business memo + 90-second verbal version | `docs/` (in progress) |

## Rebuild from scratch

1. Download `train.csv` from Kaggle into `data/raw/` (gitignored).
2. In DB Browser for SQLite, create `data/cross_sell.db` and import `train.csv` as table `train`, plus the two CSVs in `data/reference/`.
3. Run `sql/01_profile.sql` (diagnostics only) and `sql/02_clean.sql` (creates `train_cleaned`).
4. Set up a SQLite ODBC DSN named `cross_sell` pointing at the `.db`, open the `.pbix`, and Refresh.
5. Export the engineered table with DAX Studio: connect to the open pbix, run `EVALUATE 'train_cleaned'`, output to `data/processed/engineered.csv` (gitignored, ~60 MB).
6. Python: `python -m venv .venv`, activate, `pip install -r requirements.txt`.

## Constraint

There is no real customer base behind this. No dollar or percentage impact figures are claimed. Success is methodological — the model beats random targeting on a held-out test set — and validating against real outcome data is noted as the limitation.

## Notes

`docs/00_learning_log.md` is a running list of concepts learned and decisions made, written for interview prep.

# Progress

| # | Phase | Status | Where |
|---|---|---|---|
| 1 | Data acquisition | done | `data/raw/train.csv` (Kaggle, downloaded by hand) |
| 2 | Synthetic reference tables | done | `data/reference/`, `docs/03_reference_tables.md` |
| 3 | SQL profiling + cleanup | done | `sql/`, `docs/02_data_quality_log.md` |
| 4 | Power Query merges + features | done | `.pbix`, `powerquery/*.m`, `python/02_build_features.py` (matches PBI export cell for cell) |
| 5 | Model | in progress | EDA in `python/01_train_score.py` |
| 6 | Power BI model + DAX | not started | |
| 7 | Write-up | not started | |

**Next step:** Phase 5 — train logistic regression + tree model, evaluate on held-out set, export `customer_scores.csv`.

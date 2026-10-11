# Progress

| # | Phase | Status | Where |
|---|---|---|---|
| 1 | Data acquisition | done | `data/raw/train.csv` (Kaggle, downloaded by hand) |
| 2 | Synthetic reference tables | done | `data/reference/`, `docs/03_reference_tables.md` |
| 3 | SQL profiling + cleanup | done | `sql/`, `docs/02_data_quality_log.md` |
| 4 | Power Query merges + features | done | `.pbix`, `powerquery/*.m`, `python/02_build_features.py` (matches PBI export cell for cell) |
| 5 | Model | done | `python/03_train_score.py`, `reports/`, `data/processed/customer_scores.csv` (LR, test AUC 0.853, top-20% lift 2.8x) |
| 6 | Power BI model + DAX | not started | |
| 7 | Write-up | not started | |

**Next step:** Phase 6 — DAX measures, relationship diagram and dashboard spec in `dax/`.

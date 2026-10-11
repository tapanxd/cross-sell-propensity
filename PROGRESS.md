# Progress

| # | Phase | Status | Where |
|---|---|---|---|
| 1 | Data acquisition | done | `data/raw/train.csv` (Kaggle, downloaded by hand) |
| 2 | Synthetic reference tables | done | `data/reference/`, `docs/03_reference_tables.md` |
| 3 | SQL profiling + cleanup | done | `sql/`, `docs/02_data_quality_log.md` |
| 4 | Power Query merges + features | done | `.pbix`, `powerquery/*.m`, `python/02_build_features.py` (matches PBI export cell for cell) |
| 5 | Model | done | `python/03_train_score.py`, `reports/`, `data/processed/customer_scores.csv` (LR, test AUC 0.853, top-20% lift 2.8x) |
| 6 | Power BI model + DAX | spec done; **pbix assembly by hand pending** | `dax/`, `docs/powerbi_steps.md`, `reports/dax_check_values.md` |
| 7 | Write-up | done | `README.md`, `docs/summary.md`, `docs/interview_notes.md` |

**Next step (by hand):**
1. Build the dashboard in Power BI Desktop following `docs/powerbi_steps.md`; check every measure against `reports/dax_check_values.md`.
2. Say the 90-second version in `docs/interview_notes.md` out loud, timed.

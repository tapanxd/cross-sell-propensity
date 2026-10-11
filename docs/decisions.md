# Decisions log

One line each: what was chosen and why. Earlier decisions (Phases 1–3, made by hand) are in `docs/00_learning_log.md`; this file starts at the switch to builder mode.

- Kept the existing `region_map` / `channel_map` instead of the `dim_region` / `dim_channel` spec in CLAUDE.md (branch_count, cost tier, deliberate imperfections) — they are already built, verified (0 orphans) and baked into the .pbix; regenerating them would break finished work.
- Power Query M in `powerquery/` is reconstructed from the steps built in Power BI Desktop, because the .pbix stores M compressed inside `DataModel` and it can't be extracted. It is verified by rebuilding the same transforms in pandas and diffing against the Desktop export (`engineered.csv`).
- Used the global Python 3.13 install (pandas 2.3, scikit-learn 1.6, matplotlib 3.10) because no `.venv` exists; pinned those versions in `requirements.txt` so the results reproduce.
- Left `sql/03_buckets.sql` as written. Note: its `WHERE Annual_Premium > 2630` line is commented out, so it reproduces the *unfiltered* cuts (26K/32K/36K). The cuts actually used (30K/38K) came from the filtered version.

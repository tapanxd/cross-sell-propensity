# Power Query — click-by-click rebuild

You already built this by hand in `data/processed/cross_sell.pbix`. Use these steps only to rebuild it in a fresh file, or to check yours against the scripts in `powerquery/`.

## 0. One-time setup
1. Install the 64-bit SQLite ODBC driver (`sqliteodbc_w64.exe`, Christian Werner).
2. Start menu → **ODBC Data Sources (64-bit)** → User DSN → Add → *SQLite3 ODBC Driver* → name `cross_sell`, database `data/cross_sell.db`.

## 1. Create the three queries
1. Power BI Desktop → **Home → Get data → Blank query**. Repeat 3 times.
2. For each, **Home → Advanced Editor**, delete the contents, paste the matching file, click Done, and rename the query (right-click → Rename) to exactly:
   - `region_map` ← `powerquery/region_map.m`
   - `channel_map` ← `powerquery/channel_map.m`
   - `train_cleaned` ← `powerquery/train_cleaned.m`
3. If prompted for credentials: **Default or Custom**, leave everything blank, Connect.
4. Paste the two reference queries **first**, because `train_cleaned` refers to them by name.

## 2. Check it
- Select `train_cleaned`. Bottom-left: switch "Column profiling based on top 1000 rows" to **entire data set**.
- View → **Column profile**, click `id`: Count = **381,109**, Distinct = **381,109**, Error = 0.
- Click `Premium Band`: base 64,877 (17%). `Channel Group`: 11 distinct values, Other = 30,805 (8%).

## 3. Load and export
1. **Home → Close & Apply**. Save the .pbix.
2. Open DAX Studio → connect to the open .pbix → query `EVALUATE 'train_cleaned'` → Results → **File** → Run (F5) → save as CSV at `data/processed/engineered.csv`. (The table-visual "Export data" option caps at 30,000 rows, so it can't be used.)
3. Run `python python/02_build_features.py`. The last line should say *pandas output matches the Power Query export cell for cell*.

## What the UI produces vs. the scripts
The scripts are formatted and commented by hand, but every step has the same name as the step the UI creates (`Merged Queries`, `Added Conditional Column`, …), so Applied Steps will look identical.

# Phase 4 — Power Query: merges and feature engineering

## What was done
- `train_cleaned` (381,109 customers) was **left-joined** to `region_map` and `channel_map`, adding region name, zone, area type, channel name and channel type.
- Three columns were added: **Tenure Band**, **Premium Band**, **Channel Group**.
- Exported to `data/processed/engineered.csv` for the model.
- The same steps were written as M scripts (`powerquery/`) and rebuilt in pandas (`python/02_build_features.py`). The two outputs match exactly.

## Why this way
- **Left join, `train_cleaned` as the base.** Every customer must survive the join. Inner join gives the same result *today* (0 orphan codes), but if a new channel code appears upstream it would silently drop those customers. Left join keeps them, with a blank channel name you can spot.
- **Tenure: < 90 / < 180 / rest.** `Vintage` is flat between 10 and 299 days, so there's no natural break to find. The cuts are business ones instead: first quarter and half year.
- **Premium: base / low / medium / high.** 17% of customers pay exactly ₹2,630, which is a floor price. It gets its own band and is checked first. Low/medium/high split the remaining customers into thirds (30K and 38K, rounded). Putting the floor in "low" would have made "low" 45% of everyone.
- **Channel Group: top 10 + Other.** 155 codes is unusable on a slicer. The top 10 cover 92% of customers.

## Key concept: fan-out
A left join keeps every row of the base table. It can still **add** rows: if `region_map` had code 28 listed twice, every region-28 customer would match both rows and be counted twice. That's why the check is "count = 381,109 **and** distinct id = 381,109", not just the count. In pandas, `merge(..., validate="many_to_one")` raises an error if this happens.

## Check it yourself
- `python python/02_build_features.py` → prints `381,109` before and after the merges, then "matches the Power Query export cell for cell".
- In Power Query, Column profile on `id` (entire data set): Count = Distinct = 381,109.

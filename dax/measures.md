# DAX — measures and calculated columns

Paste these into the model described in `dax/model.md`. Expected values for each one are in `reports/dax_check_values.md`. If your card shows a different number, the measure or the relationship is wrong.

Tables: `train_cleaned` (one row per customer, from Power Query) and `customer_scores` (one row per customer, from Python), joined 1:1 on `id`.

---

## 1. Measure or calculated column?

| | Calculated column | Measure |
|---|---|---|
| Computed | once, at refresh, row by row | every time a visual draws, for the current filters |
| Stored | yes (uses memory) | no |
| Use for | a fixed attribute of a row: a sort key, a category | a number that depends on what's selected: totals, rates, lifts |

Every number on the dashboard is a **measure**. Columns are only used for sort keys (and the optional join date). "Response rate" as a column would be 0 or 1 on every row, which is meaningless. As a measure it's the rate for whatever is filtered.

---

## 2. Calculated columns (sort keys)

Text sorts alphabetically, which puts tiers in the order High, Low, Medium. A numeric sort key fixes that.

**Table `customer_scores`** → Table tools → New column:
```dax
Tier Sort =
SWITCH ( customer_scores[tier], "High", 1, "Medium", 2, "Low", 3 )
```
Then select `tier` → Column tools → **Sort by column** → `Tier Sort`.

**Table `train_cleaned`**:
```dax
Vehicle Age Sort =
SWITCH ( train_cleaned[Vehicle_Age], "< 1 Year", 1, "1-2 Year", 2, "> 2 Years", 3 )
```
`Vehicle_Age` → Sort by column → `Vehicle Age Sort`. (It's an ordinal category, noted back in Phase 2.)

```dax
Premium Band Sort =
SWITCH ( train_cleaned[Premium Band], "base", 1, "low", 2, "medium", 3, "high", 4 )
```
`Premium Band` → Sort by column → `Premium Band Sort`.

Hide all three sort columns (right-click → Hide in report view).

---

## 3. Measures

Create a home for them: **Home → Enter data** → name the table `_Measures` → Load. Create each measure with that table selected (**Home → New measure**). Once a measure exists, delete the dummy `Column1`. The table then shows a calculator icon and sits at the top of the field list.

### Counts and rates

```dax
Customers =
COUNTROWS ( train_cleaned )
```
How many customers are in the current filter. → 381,109 unfiltered.

```dax
Responders =
SUM ( train_cleaned[Response] )
```
`Response` is 0/1, so the sum is the number of yes. → 46,710.

```dax
Response Rate =
DIVIDE ( [Responders], [Customers] )
```
`DIVIDE` returns blank instead of an error when a slice has 0 customers. → 12.26%.

### Test-set versions (validation measures)
The model saw the train rows during training, so its performance is only judged on the 76,222 test customers.

```dax
Test Customers =
CALCULATE ( [Customers], customer_scores[split] = "test" )
```

```dax
Test Responders =
CALCULATE ( [Responders], customer_scores[split] = "test" )
```

```dax
Test Response Rate =
DIVIDE ( [Test Responders], [Test Customers] )
```
**What CALCULATE does here:** it evaluates `[Customers]` again, with one extra filter added: `split = "test"`. Every filter already coming from the visual (tier, zone, slicers) stays. The filter lands on `customer_scores`, and the 1:1 relationship carries it across to `train_cleaned`, where the rows are counted.

### Lift over random targeting

Plain-English logic first. If you called customers **at random** from the current slice (say Peel), your yes-rate would be Peel's overall yes-rate. If you call only Peel's **High** tier, your yes-rate is the High-tier rate. Lift = High-tier rate ÷ random rate.

```dax
Baseline Response Rate =
CALCULATE ( [Test Response Rate], REMOVEFILTERS ( customer_scores[tier] ) )
```
**What CALCULATE does here:** it *removes* the tier filter and keeps everything else. On a tier row it gives the rate across all tiers, which is the "call at random" rate for the same zone/channel slice. → 12.26% unfiltered, 9.47% with zone = Peel.

```dax
Lift vs Random =
DIVIDE ( [Test Response Rate], [Baseline Response Rate] )
```
→ High 2.82, Medium 1.39, Low 0.03. With no tier filter it's exactly 1 (random vs itself).

```dax
High Tier Lift =
CALCULATE ( [Lift vs Random], customer_scores[tier] = "High" )
```
Lift of the High tier inside whatever zone/region/channel the visual is showing. Inside the CALCULATE the tier is set to High, but `Baseline Response Rate` still removes the tier filter. So the comparison is High vs. all tiers *in that region*. → Peel 3.62, Toronto 2.41.

### Shares (how concentrated the opportunity is)

```dax
Share of Customers =
DIVIDE ( [Customers], CALCULATE ( [Customers], REMOVEFILTERS ( customer_scores[tier] ) ) )
```
→ High 20.2%, Medium 29.9%, Low 49.9%.

```dax
Share of Responders Captured =
DIVIDE ( [Test Responders], CALCULATE ( [Test Responders], REMOVEFILTERS ( customer_scores[tier] ) ) )
```
Of all the test customers who said yes, the share that sits in this tier. → High 57.2%, Medium 41.6%, Low 1.3%.

```dax
High Tier Customers =
CALCULATE ( [Customers], customer_scores[tier] = "High" )
```
→ 76,828. This is the size of the call list.

```dax
High Tier Share =
DIVIDE ( [High Tier Customers], [Customers] )
```
Share of a region's or channel's customers that are High tier.

### Model-based opportunity
These use the model's probabilities. They're **model expectations under the conditions of the original campaign**, not revenue or money, and they should be labelled that way.

```dax
Expected Responders =
SUM ( customer_scores[probability] )
```
Sum of everyone's probability = how many yes the model expects in the slice. → 46,734 unfiltered vs 46,710 actual. That's a calibration check: they should be close.

```dax
Expected Responders (High) =
CALCULATE ( [Expected Responders], customer_scores[tier] = "High" )
```
→ Toronto 19,171, Peel 3,610.

```dax
Avg Propensity =
AVERAGE ( customer_scores[probability] )
```

```dax
Avg Propensity (Test) =
CALCULATE ( [Avg Propensity], customer_scores[split] = "test" )
```
Put this next to `Test Response Rate` by tier. Predicted vs actual should match (High 34.66% vs 34.60%).

### Formatting (Measure tools → Format)
- Percentage, 1 decimal: Response Rate, Test Response Rate, Baseline Response Rate, Share of Customers, Share of Responders Captured, High Tier Share, Avg Propensity, Avg Propensity (Test).
- Whole number with thousands separator: Customers, Responders, Test Customers, Test Responders, High Tier Customers, Expected Responders, Expected Responders (High).
- Lift vs Random, High Tier Lift → Custom format string `0.00"x"`.

---

## 4. Optional: time intelligence (skill demo, not on the main pages)

The dataset has no dates, only `Vintage` (days as a customer). Turning that into a join date needs an **assumed snapshot date**, which is invented. Phase 5 also showed tenure has no predictive signal. So this is here to practise the functions only. Keep it off the stakeholder pages and label it as illustrative if you show it.

```dax
-- calculated column on train_cleaned; set its data type to Date
Join Date =
DATE ( 2024, 12, 31 ) - train_cleaned[Vintage]
```
```dax
-- calculated table: Modeling -> New table; then Table tools -> Mark as date table (column Date)
Dates =
CALENDAR ( DATE ( 2024, 1, 1 ), DATE ( 2024, 12, 31 ) )
```
Relationship: `Dates[Date]` (1) → `train_cleaned[Join Date]` (*), single direction.
```dax
Customers Joined YTD =
TOTALYTD ( [Customers], Dates[Date] )
```
```dax
Customers Joined Last 90 Days =
CALCULATE ( [Customers], DATESINPERIOD ( Dates[Date], MAX ( Dates[Date] ), -90, DAY ) )
```
Check: in a line chart with `Dates[Date]` by month, YTD should climb to 381,109 at December.

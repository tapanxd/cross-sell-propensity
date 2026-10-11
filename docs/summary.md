# Cross-sell prioritisation: who to offer vehicle insurance first

**To:** VP of Distribution  **Re:** Ranking our single-product (health) customers for a vehicle-insurance offer

## Recommendation
1. **Call the High tier first.** It's 1 in 5 customers. In a held-out test, 34.6% of them accepted, against 12.3% if you call at random: **2.8× the hit-rate**. That one-fifth of the base holds **57% of everyone who said yes**.
2. **Stop pitching the Low tier.** It's half of all customers, and only **0.3%** of them accepted in the test. These are almost entirely people who already have vehicle insurance elsewhere, or have never had vehicle damage.
3. **Use the Medium tier to extend the campaign** if capacity allows. Its yes-rate is 17%, still above random, and High + Medium together hold 99% of the yeses.
4. **Prioritise ranking hardest outside Toronto.** Toronto has most of the High-tier customers, but in Durham, Peel and York the High tier does 3.6–4.2× better than random calling there. A ranked list adds the most where random calling does worst.

## What we were asked
Most customers hold one policy. Sales reaches out but can't tell who's likely to take a second product. The ask: identify those customers so the channels can target them directly.

## What we found
Using a past campaign where 381,109 health-policy customers were offered vehicle insurance (12.3% accepted):
- **Two facts decide most of it.** Customers already insured elsewhere almost never accept (0.09%). Customers with past vehicle damage accept at 24%, versus 0.5% without.
- **Older vehicles and mid-life customers respond more.** Vehicles over 2 years old: 29%. Ages 30–49: around 21%, against 4% in their twenties.
- **How long someone has been a customer doesn't matter.** The yes-rate is the same 12% for new and long-standing customers.
- **Channel matters a lot.** The agent and bank-partner channels hold nearly three-quarters (73%) of the High tier. The largest channel (web/aggregator, a third of customers) has no High-tier customers.

## How the ranking was built (briefly)
SQL cleaning, then Power Query to join region/channel reference data, then a logistic regression model that gives every customer a probability of accepting. The model was checked on 76,222 customers it never saw during training (ROC-AUC 0.85). Its probabilities match actual yes-rates tier by tier, so "34% likely" means what it says. The full list, by region and channel, is in the Power BI dashboard ("Call list" page).

## Before acting on it: what this does and doesn't show
- **This is one historical campaign from a public dataset, not our own customer history.** The patterns are real for that campaign. Whether they hold for our customers, offer and timing is unproven.
- **No revenue or cost figures are claimed.** The analysis ranks likelihood to accept. It doesn't estimate premium value, call cost or profit.
- **Channel effects can't be separated from customer mix.** Web/aggregator customers may respond poorly because of the channel, or because of *who* comes through it. Only a test can tell those apart.
- **Region and channel names are illustrative labels** for the dataset's codes.

## How to validate with real data (proposed next step)
1. **Controlled pilot.** In each region, randomly split High-tier customers into "call" and "don't call (yet)". Also call a small random sample of Medium and Low customers. Compare acceptance between groups. That measures real lift instead of assuming it.
2. **Add the money.** Join pilot results to premium and cost-per-call to see whether the High tier is also the most *profitable* to call, not just the most likely to say yes.
3. **Re-check monthly.** Compare predicted vs actual acceptance by tier (a dashboard page already shows this). If they drift apart, retrain.

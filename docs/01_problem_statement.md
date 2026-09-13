# Phase 1 — Problem Statement

## Stakeholder version (VP of Distribution)

Most customers only have one policy with us. We need them to hold two or three products — that's what gives us customer retention. The sales team reaches out to people, but they can't filter down to the customers who are actually likely to buy more from us. I need to know who those customers are, so our sales channels can target them directly and close more than they do calling people blind today.

## Analytical version

Health-policy holders are our "one product" customers and vehicle insurance is the "second product." We have data on customers who were previously pitched vehicle insurance, along with whether they said yes or no. We'll learn the pattern that separates yes from no, and use it to rank existing health-policy customers by how likely each is to accept. The output is a ranked, tiered list (customer ID, predicted probability, high/medium/low tier) the sales team can use to decide who to call first. To check the ranking is trustworthy, a stratified slice of the historical data is held out from training and used only to evaluate whether the model finds the "yes" customers better than chance.

## What "success" looks like

There is no real revenue or response data behind this project, so success is methodological, not financial: the model beats random targeting on the held-out test set (measured with precision/recall/ROC-AUC, not accuracy, because of the ~12% positive rate), and the dashboard lets a stakeholder see that lift broken down by region and channel. No dollar or percentage impact figures are claimed; validating with real outcome data is noted as a limitation.

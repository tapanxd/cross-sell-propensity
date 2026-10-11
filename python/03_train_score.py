"""
Phase 5: train, evaluate and score.

1. Stratified 80/20 split (the 20% test set stands in for "customers we haven't called yet").
2. Two models, both with class_weight='balanced' for the 12% imbalance:
     - logistic regression (interpretable baseline)
     - histogram gradient boosting (tree-based comparison)
   Compared by 5-fold cross-validated ROC-AUC on the TRAIN set only, so the test set is never used to choose.
   Logistic regression is kept unless the tree beats it by more than 0.01 AUC (interpretability first).
3. Winner is calibrated (isotonic) so its scores are honest probabilities, not inflated by the weighting.
4. Test-set evaluation: ROC-AUC, average precision, precision/recall, lift over random targeting.
5. Tiers from train-set score quantiles: High = top 20%, Medium = next 30%, Low = bottom 50%.
6. Score every customer -> data/processed/customer_scores.csv (id, probability, tier, split, rank).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # write plots to files, no window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss, classification_report,
                             precision_recall_curve, roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
FIG = REPORTS / "figures"
FIG.mkdir(parents=True, exist_ok=True)
SEED = 42

# ---------------------------------------------------------------- load
# Prefer the Power Query export (design.md data flow); fall back to the pandas mirror.
src = PROC / "engineered.csv"
if not src.exists():
    src = PROC / "engineered_pandas.csv"
df = pd.read_csv(src)
print(f"loaded {src.name}: {len(df):,} rows")
assert df["id"].is_unique and df.notna().all().all()

# Age has a hump (low in the 20s, peak 30-49, falls after 60). A straight-line model can't fit a hump
# from raw Age, so logistic regression gets 10-year age bands; the tree model gets raw Age.
df["Age Band"] = pd.cut(df["Age"], bins=range(20, 100, 10), right=False,
                        labels=[f"{a}-{a+9}" for a in range(20, 90, 10)]).astype(str)

# Features chosen from the EDA in 01_train_score.py (docs/decisions.md lists what was left out and why)
CAT_COMMON = ["Gender", "Vehicle_Age", "Vehicle_Damage", "region_name", "Channel Group"]
BINARY = ["Previously_Insured", "Driving_License"]
y = df["Response"]  # the label -- used only as the target, never as an input

X_cols = CAT_COMMON + BINARY + ["Age", "Age Band", "Annual_Premium"]
X = df[X_cols]

# ---------------------------------------------------------------- split
# stratify=y keeps the 12.26% yes-rate identical in train and test
X_train, X_test, y_train, y_test, id_train, id_test = train_test_split(
    X, y, df["id"], test_size=0.2, stratify=y, random_state=SEED)
print(f"train {len(X_train):,} (yes {y_train.mean():.2%}) | test {len(X_test):,} (yes {y_test.mean():.2%})")

# ---------------------------------------------------------------- models
# Logistic regression: one-hot the categories, log + scale the premium (it runs 2.6K-540K, heavily skewed).
# Everything sits inside a Pipeline, so the scaler/encoder are fitted on training folds only (no leakage).
logreg = Pipeline([
    ("prep", ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", drop="if_binary"), CAT_COMMON + ["Age Band"]),
        ("bin", "passthrough", BINARY),
        ("prem", Pipeline([("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
                            ("scale", StandardScaler())]),
         ["Annual_Premium"]),
    ])),
    ("model", LogisticRegression(class_weight="balanced", max_iter=2000)),
])

# Gradient boosting: trees don't need scaling or one-hot; categories are just numbered and flagged
# as categorical so the trees can split on them directly.
hgb = Pipeline([
    ("prep", ColumnTransformer([
        ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), CAT_COMMON),
        ("num", "passthrough", BINARY + ["Age", "Annual_Premium"]),
    ])),
    ("model", HistGradientBoostingClassifier(
        categorical_features=list(range(len(CAT_COMMON))),  # first block of columns = categories
        class_weight="balanced", learning_rate=0.05, max_iter=400, random_state=SEED)),
])
models = {"logistic_regression": logreg, "gradient_boosting": hgb}

# ---------------------------------------------------------------- choose (train only)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
cv_auc = {}
for name, m in models.items():
    s = cross_val_score(m, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
    cv_auc[name] = (s.mean(), s.std())
    print(f"CV ROC-AUC {name:20s} {s.mean():.4f} +/- {s.std():.4f}")
# Prefer the interpretable model: logistic regression wins unless the tree is better by more than
# 0.01 AUC. Its coefficients explain the ranking to a stakeholder; a black box has to earn its place.
MIN_GAIN_FOR_TREE = 0.01
gap = cv_auc["gradient_boosting"][0] - cv_auc["logistic_regression"][0]
best_name = "gradient_boosting" if gap > MIN_GAIN_FOR_TREE else "logistic_regression"
print(f"-> tree gain over logistic regression: {gap:+.4f} AUC -> selected: {best_name}")

# ---------------------------------------------------------------- test-set evaluation, both models
results, test_scores = {}, {}
for name, m in models.items():
    m.fit(X_train, y_train)
    p = m.predict_proba(X_test)[:, 1]
    test_scores[name] = p
    results[name] = {
        "cv_roc_auc_mean": round(cv_auc[name][0], 4),
        "cv_roc_auc_std": round(cv_auc[name][1], 4),
        "test_roc_auc": round(roc_auc_score(y_test, p), 4),
        "test_average_precision": round(average_precision_score(y_test, p), 4),
    }
    # At the default 0.5 cut-off, what does the balanced model flag? (precision vs recall trade-off)
    print(f"\n{name} @ 0.5 threshold (test):\n" +
          classification_report(y_test, (p >= 0.5).astype(int), digits=3, target_names=["no", "yes"]))

# ---------------------------------------------------------------- calibrate the winner
# class_weight='balanced' pushes scores up (average near 0.5 instead of 0.12). Isotonic calibration maps
# them back to real yes-rates without changing the order -- so tiers are unaffected but
# "probability" in the export means what it says.
final = CalibratedClassifierCV(models[best_name], method="isotonic", cv=5)
final.fit(X_train, y_train)
p_test = final.predict_proba(X_test)[:, 1]
p_train = final.predict_proba(X_train)[:, 1]

# ---------------------------------------------------------------- lift / gains on the test set
base_rate = y_test.mean()
order = np.argsort(-p_test)                   # customers ranked best-first
y_sorted = y_test.to_numpy()[order]
cum_yes = np.cumsum(y_sorted)
gains = {}
for pct in (10, 20, 30, 50):
    k = int(len(y_sorted) * pct / 100)
    rate = y_sorted[:k].mean()
    gains[f"top_{pct}pct"] = {
        "response_rate": round(float(rate), 4),
        "lift_vs_random": round(float(rate / base_rate), 2),   # times better than calling at random
        "share_of_all_yes_captured": round(float(cum_yes[k - 1] / cum_yes[-1]), 4),
    }

# ---------------------------------------------------------------- tiers
# Cut-points come from the TRAIN score distribution, then are applied unchanged to everyone.
# Top 20% = High (a plausible one-campaign call budget); bottom 50% = Low (it mostly holds the
# already-insured / no-damage customers whose yes-rate is near zero).
t_high = float(np.quantile(p_train, 0.80))
t_med = float(np.quantile(p_train, 0.50))


def to_tier(p):
    return np.where(p >= t_high, "High", np.where(p >= t_med, "Medium", "Low"))


test_tiers = pd.DataFrame({"tier": to_tier(p_test), "y": y_test.to_numpy(), "p": p_test})
tier_table = (test_tiers.groupby("tier")
              .agg(customers=("y", "size"), responders=("y", "sum"),
                   actual_rate=("y", "mean"), mean_probability=("p", "mean"))
              .reindex(["High", "Medium", "Low"]))
tier_table["share_of_customers"] = tier_table["customers"] / tier_table["customers"].sum()
tier_table["share_of_responders"] = tier_table["responders"] / tier_table["responders"].sum()
tier_table["lift_vs_random"] = tier_table["actual_rate"] / base_rate
print("\nTiers on the TEST set:\n" + tier_table.round(4).to_string())

# ---------------------------------------------------------------- score everyone & export
p_all = final.predict_proba(X)[:, 1]
scores = pd.DataFrame({
    "id": df["id"],
    "probability": p_all.round(6),
    "tier": to_tier(p_all),
    # split lets the dashboard measure lift on test rows only (train rows were seen in training)
    "split": np.where(df["id"].isin(set(id_test)), "test", "train"),
})
scores["rank"] = scores["probability"].rank(ascending=False, method="first").astype(int)
out = PROC / "customer_scores.csv"
scores.to_csv(out, index=False)
assert len(scores) == len(df) and scores["id"].is_unique
print(f"\nwrote {out.relative_to(ROOT)}: {len(scores):,} rows; tiers = "
      f"{scores['tier'].value_counts().to_dict()}")

# ---------------------------------------------------------------- interpretability (logistic regression)
lr = models["logistic_regression"]
names = lr.named_steps["prep"].get_feature_names_out()
coefs = pd.Series(lr.named_steps["model"].coef_[0], index=names).sort_values()
coefs.to_csv(REPORTS / "logreg_coefficients.csv", header=["coefficient"])

# ---------------------------------------------------------------- plots
fig, ax = plt.subplots(figsize=(5.5, 5))
for name, p in test_scores.items():
    fpr, tpr, _ = roc_curve(y_test, p)
    ax.plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(y_test, p):.3f})")
ax.plot([0, 1], [0, 1], "k--", lw=1, label="random")
ax.set(xlabel="False positive rate", ylabel="True positive rate (recall)", title="ROC - test set")
ax.legend(loc="lower right"); fig.tight_layout(); fig.savefig(FIG / "roc.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.5, 5))
for name, p in test_scores.items():
    prec, rec, _ = precision_recall_curve(y_test, p)
    ax.plot(rec, prec, label=f"{name} (AP {average_precision_score(y_test, p):.3f})")
ax.axhline(base_rate, color="k", ls="--", lw=1, label=f"random ({base_rate:.1%})")
ax.set(xlabel="Recall", ylabel="Precision", title="Precision-recall - test set")
ax.legend(); fig.tight_layout(); fig.savefig(FIG / "precision_recall.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.5, 5))
x = np.arange(1, len(y_sorted) + 1) / len(y_sorted)
ax.plot(x, cum_yes / cum_yes[-1], label=f"model ({best_name})")
ax.plot([0, 1], [0, 1], "k--", lw=1, label="random targeting")
ax.axvline(0.2, color="grey", lw=0.8)
ax.set(xlabel="Share of customers contacted (best first)", ylabel="Share of all yes captured",
       title="Cumulative gains - test set")
ax.legend(loc="lower right"); fig.tight_layout(); fig.savefig(FIG / "cumulative_gains.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.5, 5))
frac_pos, mean_pred = calibration_curve(y_test, p_test, n_bins=10, strategy="quantile")
ax.plot(mean_pred, frac_pos, "o-", label="calibrated model")
lim = max(mean_pred.max(), frac_pos.max()) * 1.05
ax.plot([0, lim], [0, lim], "k--", lw=1, label="perfect")
ax.set(xlabel="Predicted probability", ylabel="Actual yes-rate", title="Calibration - test set")
ax.legend(); fig.tight_layout(); fig.savefig(FIG / "calibration.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.5, 4))
ax.bar(tier_table.index, tier_table["actual_rate"] * 100, color=["#2b6cb0", "#63a4d9", "#c3d9ee"])
ax.axhline(base_rate * 100, color="k", ls="--", lw=1, label=f"random ({base_rate:.1%})")
for i, v in enumerate(tier_table["actual_rate"] * 100):
    ax.text(i, v + 0.5, f"{v:.1f}%", ha="center")
ax.set(ylabel="Actual yes-rate (%)", title="Yes-rate by tier - test set"); ax.legend()
fig.tight_layout(); fig.savefig(FIG / "response_by_tier.png", dpi=130); plt.close(fig)

fig, ax = plt.subplots(figsize=(7, 6))
top = pd.concat([coefs.head(8), coefs.tail(8)])
ax.barh(top.index.str.replace(r"^\w+__", "", regex=True), top.values,
        color=["#c0392b" if v < 0 else "#2b6cb0" for v in top.values])
ax.set(xlabel="Coefficient (log-odds)", title="Logistic regression: strongest effects")
fig.tight_layout(); fig.savefig(FIG / "logreg_coefficients.png", dpi=130); plt.close(fig)

# ---------------------------------------------------------------- save metrics
metrics = {
    "source": src.name, "rows": len(df), "test_rows": len(y_test),
    "test_base_rate": round(float(base_rate), 4),
    "models": results, "selected": best_name, "selection_rule": f"tree only if CV AUC gain > {MIN_GAIN_FOR_TREE}",
    "final_calibrated": {
        "test_roc_auc": round(roc_auc_score(y_test, p_test), 4),
        "test_average_precision": round(average_precision_score(y_test, p_test), 4),
        "test_brier": round(brier_score_loss(y_test, p_test), 4),
        "mean_predicted_probability_test": round(float(p_test.mean()), 4),
    },
    "gains_test": gains,
    "tier_thresholds": {"high_if_probability_at_least": round(t_high, 6),
                        "medium_if_probability_at_least": round(t_med, 6)},
    "tiers_test": tier_table.round(4).reset_index().to_dict(orient="records"),
}
(REPORTS / "metrics.json").write_text(json.dumps(metrics, indent=2))
print("\n" + json.dumps({k: metrics[k] for k in ["final_calibrated", "gains_test", "tier_thresholds"]}, indent=2))

import numpy as np
import pandas as pd

# 1. Load the dataset
df = pd.read_csv("data/processed/engineered.csv")

# 2. Bucket the 'Age' column into 10-year intervals (e.g., 20–29, 30–39, etc.)
# Creates bins based on the minimum and maximum age in the dataset
min_age = int(np.floor(df["Age"].min() / 10) * 10)
max_age = int(np.ceil(df["Age"].max() / 10) * 10)
bins = list(range(min_age, max_age + 10, 10))
labels = [f"{bins[i]}-{bins[i]+9}" for i in range(len(bins) - 1)]

df["Age_Bucket"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)

# 3. List of columns to evaluate (including the new Age_Bucket)
columns_to_group = [
    "Previously_Insured",
    "Vehicle_Damage",
    "Vehicle_Age",
    "Gender",
    "Premium Band",
    "Tenure Band",
    "channel_type",
    "zone",
    "area_type",
    "Age_Bucket",
]

# 4. Loop through each column and compute the mean (yes-rate) and row count
for col in columns_to_group:
    if col in df.columns:
        print(f"\n========================================")
        print(f"Groupby Summary: {col}")
        print(f"========================================")

        # Aggregate mean (yes-rate) and total row count
        summary = (
            df.groupby(col)["Response"]
            .agg(yes_rate="mean", total_count="count")
            .reset_index()
        )

        # Format yes-rate as percentage for easier reading (optional)
        summary["yes_rate"] = summary["yes_rate"].apply(lambda x: f"{x:.2%}")

        print(summary.to_string(index=False))
    else:
        print(f"\nColumn '{col}' not found in the DataFrame.")
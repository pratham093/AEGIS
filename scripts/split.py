import pandas as pd
from datetime import datetime


df = pd.read_csv("merged_data.csv")

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values(["asset", "Date"]).reset_index(drop=True)


split_date = datetime(2024, 1, 1)


train_df = df[df["Date"] < split_date]
test_df  = df[df["Date"] >= split_date]

train_df.to_csv("train_data.csv", index=False)
test_df.to_csv("test_data.csv", index=False)

print(f"[✓] Training data: {len(train_df)} rows")
print(f"[✓] Testing data: {len(test_df)} rows")

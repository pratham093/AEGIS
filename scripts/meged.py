import os
import pandas as pd

STRUCTURED_DIR = "STRUCTURED"
OUTPUT_FILE = "merged_data.csv"

def merge_all_structured():
    merged_df = []

    for file in os.listdir(STRUCTURED_DIR):
        if file.endswith(".csv"):
            file_path = os.path.join(STRUCTURED_DIR, file)
            df = pd.read_csv(file_path)

            # Add 'asset' column from filename (e.g., AAPL.csv → AAPL)
            asset_name = file.replace(".csv", "")
            df['asset'] = asset_name

            merged_df.append(df)

    if merged_df:
        final_df = pd.concat(merged_df, ignore_index=True)
        final_df.dropna(inplace=True)  # optional: drop rows with missing values
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"[✓] Merged file saved to {OUTPUT_FILE}")
    else:
        print("[!] No CSV files found in STRUCTURED folder.")

if __name__ == "__main__":
    merge_all_structured()

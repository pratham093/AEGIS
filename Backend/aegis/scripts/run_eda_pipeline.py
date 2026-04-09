"""Run the full data-prep pipeline: fetch, features, EDA."""

import subprocess
import sys

steps = [
    ("1. Fetching Data", [sys.executable, "-m", "aegis.pipelines.build_dataset"]),
    ("2. Engineering Features", [sys.executable, "-m", "aegis.pipelines.feature_engineering"]),
    ("3. Running EDA", [sys.executable, "-m", "aegis.pipelines.eda"]),
]

if __name__ == "__main__":
    for label, cmd in steps:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"{'='*60}")
        result = subprocess.run(cmd, cwd=".")
        if result.returncode != 0:
            print(f"\n  ERROR in step: {label}")
            print("  Fix the issue and re-run.")
            sys.exit(1)

    print("\n  Pipeline complete.")

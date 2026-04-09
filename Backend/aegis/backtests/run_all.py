"""Run all asset backtests and save combined results."""

import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from aegis.backtests.core import REPORT_FIG, REPORT_MET, DATA_PROC
from aegis.backtests.spy import run_spy_backtest
from aegis.backtests.qqq import run_qqq_backtest
from aegis.backtests.iwm import run_iwm_backtest
from aegis.backtests.btc import run_btc_backtest


def plot_combined_summary(all_results):
    colors = {"SPY": "#2ecc71", "QQQ": "#3498db", "IWM": "#9b59b6", "BTC": "#f39c12"}
    assets = list(all_results.keys())
    x = range(len(assets))
    c = [colors.get(a, "#333") for a in assets]

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    axes = axes.flatten()
    for idx, (asset, res) in enumerate(all_results.items()):
        ax = axes[idx]
        rdf = res["rdf"]
        m = res["metrics"]
        ax.plot(rdf.index, rdf["cum_sized"] * 100, color=colors[asset], linewidth=1.5, label="AEGIS V3")
        ax.plot(rdf.index, rdf["cum_bh"] * 100, color="#bbb", linewidth=1, label="Buy & Hold", alpha=0.7)
        ax.fill_between(rdf.index, 0, rdf["cum_sized"] * 100, alpha=0.1, color=colors[asset])
        ax.set_title(f"{asset}  |  Sharpe: {m['sized_sharpe']:+.3f} vs {m['bh_sharpe']:+.3f}",
                     fontsize=12, fontweight="bold")
        ax.set_ylabel("Cumulative Return (%)")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    plt.suptitle("AEGIS V3 — Walk-Forward Equity Curves", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(REPORT_FIG / "v21_equity_curves.png", dpi=150, bbox_inches="tight")
    plt.close()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    aegis_sharpe = [all_results[a]["metrics"]["sized_sharpe"] for a in assets]
    bh_sharpe = [all_results[a]["metrics"]["bh_sharpe"] for a in assets]
    axes[0].bar([i - 0.15 for i in x], aegis_sharpe, 0.3, color=c, label="AEGIS V3")
    axes[0].bar([i + 0.15 for i in x], bh_sharpe, 0.3, color="#bbb", label="B&H")
    axes[0].set_xticks(list(x)); axes[0].set_xticklabels(assets)
    axes[0].set_title("Sharpe Ratio", fontweight="bold")
    axes[0].legend(); axes[0].axhline(y=0, color="black", linewidth=0.5)
    axes[0].grid(True, alpha=0.3)

    aegis_dd = [all_results[a]["metrics"]["max_dd_sized_pct"] for a in assets]
    bh_dd = [all_results[a]["metrics"]["max_dd_bh_pct"] for a in assets]
    axes[1].bar([i - 0.15 for i in x], aegis_dd, 0.3, color=c, label="AEGIS V3")
    axes[1].bar([i + 0.15 for i in x], bh_dd, 0.3, color="#bbb", label="B&H")
    axes[1].set_xticks(list(x)); axes[1].set_xticklabels(assets)
    axes[1].set_title("Max Drawdown (%)", fontweight="bold")
    axes[1].legend(); axes[1].grid(True, alpha=0.3)

    exp = [all_results[a]["metrics"]["avg_exposure_pct"] for a in assets]
    axes[2].bar(x, exp, color=c)
    axes[2].set_xticks(list(x)); axes[2].set_xticklabels(assets)
    axes[2].set_title("Avg Exposure (%)", fontweight="bold")
    axes[2].grid(True, alpha=0.3)

    plt.suptitle("AEGIS V3 — Cross-Asset Summary", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(REPORT_FIG / "v21_summary_bars.png", dpi=150, bbox_inches="tight")
    plt.close()

    print(f"\n  Saved combined figures → {REPORT_FIG}")


def save_combined_outputs(all_results):
    rows = []
    for asset, res in all_results.items():
        m = res["metrics"].copy()
        m.pop("flag_counts", None)
        rows.append(m)

    pd.DataFrame(rows).to_csv(REPORT_MET / "v21_backtest_summary.csv", index=False)

    metrics_json = {a: res["metrics"] for a, res in all_results.items()}
    with open(REPORT_MET / "v21_backtest_metrics.json", "w") as f:
        json.dump(metrics_json, f, indent=2, default=str)

    print(f"  Saved combined outputs → {REPORT_MET}")


def main():
    print("\n  Running all backtests...")

    all_results = {}

    all_results["SPY"] = run_spy_backtest()
    all_results["QQQ"] = run_qqq_backtest()
    all_results["IWM"] = run_iwm_backtest()
    all_results["BTC"] = run_btc_backtest()

    print("\n\nGenerating combined figures...")
    plot_combined_summary(all_results)

    print("\nSaving combined outputs...")
    save_combined_outputs(all_results)

    print("\n  All backtests complete:")
    for asset, res in all_results.items():
        m = res["metrics"]
        arch = "base rule"
        print(f"  {asset:4s} ({arch:9s}): Sharpe={m['sized_sharpe']:+.3f} "
              f"(B&H={m['bh_sharpe']:+.3f})  "
              f"DD={m['max_dd_sized_pct']:.1f}% "
              f"(B&H={m['max_dd_bh_pct']:.1f}%)  "
              f"Exp={m['avg_exposure_pct']:.0f}%")


if __name__ == "__main__":
    main()

"""EDA — generates plots and stats from the universe and feature datasets."""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy import stats
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# resolve paths relative to Backend/ so this works from any cwd
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # aegis/pipelines/ → Backend/
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FEATURES_DIR = BASE_DIR / "data" / "features"
FIGURES_DIR = BASE_DIR / "reports" / "figures"
METRICS_DIR = BASE_DIR / "reports" / "metrics"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("deep")
FIGSIZE_WIDE = (14, 6)
FIGSIZE_SQUARE = (10, 10)
FIGSIZE_MEDIUM = (12, 8)
DPI = 150


def load_data():
    """loads universe parquet and per-symbol feature files."""
    universe = pd.read_parquet(PROCESSED_DIR / "universe.parquet")

    features = {}

    print(f"  Looking for features in: {FEATURES_DIR}")
    print(f"  Directory exists: {FEATURES_DIR.exists()}")

    if FEATURES_DIR.exists():
        all_files = list(FEATURES_DIR.iterdir())
        print(f"  Files found: {[f.name for f in all_files]}")

        for f in FEATURES_DIR.glob("features_*.parquet"):
            # skip the combined file, we want individual symbols
            if f.stem == "features_all":
                continue
        symbol = f.stem.replace("features_", "")
        features[symbol] = pd.read_parquet(f)
    return universe, features


def generate_summary_statistics(universe: pd.DataFrame):
    """computes descriptive stats plus skewness and kurtosis for every column."""
    print("  [1/16] Summary statistics...")
    desc = universe.describe().T
    desc["missing"] = universe.isnull().sum()
    desc["missing_pct"] = (universe.isnull().sum() / len(universe) * 100).round(2)
    desc["skewness"] = universe.skew()
    desc["kurtosis"] = universe.kurtosis()
    desc.to_csv(METRICS_DIR / "summary_statistics.csv")
    print(f"       Saved summary_statistics.csv ({len(desc)} variables)")
    return desc


def plot_missing_values(universe: pd.DataFrame):
    """bar chart of missing percentages plus a heatmap of the missingness pattern."""
    print("  [2/16] Missing value analysis...")

    missing = universe.isnull().sum()
    missing_pct = (missing / len(universe) * 100).round(2)
    missing_df = pd.DataFrame({"count": missing, "percent": missing_pct})
    missing_df = missing_df[missing_df["count"] > 0].sort_values("percent", ascending=False)
    missing_df.to_csv(METRICS_DIR / "missing_values_summary.csv")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    if len(missing_df) > 0:
        cols_to_show = missing_df.head(20)
        axes[0].barh(range(len(cols_to_show)), cols_to_show["percent"], color="#e74c3c")
        axes[0].set_yticks(range(len(cols_to_show)))
        axes[0].set_yticklabels(cols_to_show.index, fontsize=9)
        axes[0].set_xlabel("Missing (%)")
        axes[0].set_title("Missing Values by Column (Top 20)")
        axes[0].invert_yaxis()
    else:
        axes[0].text(0.5, 0.5, "No missing values!", ha="center", va="center", fontsize=14)
        axes[0].set_title("Missing Values by Column")

    # downsample rows so the heatmap doesn't choke on large datasets
    sample = universe.isnull().iloc[::max(1, len(universe) // 500)]
    sns.heatmap(sample.T, cbar=False, cmap="YlOrRd", ax=axes[1], yticklabels=True)
    axes[1].set_title("Missing Data Pattern (sampled)")
    axes[1].set_xlabel("Time (sampled)")
    axes[1].tick_params(axis="y", labelsize=7)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "missing_values_heatmap.png", dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"       {len(missing_df)} columns with missing data")


def plot_price_timeseries(universe: pd.DataFrame):
    """normalized equity prices on top, bitcoin on bottom, both log-scaled."""
    print("  [3/16] Price time series...")

    instruments = ["spy", "qqq", "iwm", "btc_usd"]
    available = [i for i in instruments if i in universe.columns]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # normalize to base=100 so different price levels are comparable
    equity = [i for i in available if i != "btc_usd"]
    for inst in equity:
        series = universe[inst].dropna()
        normalized = series / series.iloc[0] * 100
        axes[0].plot(normalized.index, normalized.values, label=inst.upper(), linewidth=1.2)
    axes[0].set_ylabel("Normalized Price (base=100)")
    axes[0].set_title("Equity Index ETFs — Normalized Price History")
    axes[0].legend(loc="upper left")
    axes[0].set_yscale("log")

    if "btc_usd" in available:
        btc = universe["btc_usd"].dropna()
        axes[1].plot(btc.index, btc.values, label="BTC-USD", color="#f39c12", linewidth=1.2)
        axes[1].set_ylabel("Price (USD)")
        axes[1].set_title("Bitcoin — Price History")
        axes[1].legend(loc="upper left")
        axes[1].set_yscale("log")
    else:
        axes[1].text(0.5, 0.5, "BTC-USD not available", ha="center", va="center")

    axes[1].set_xlabel("Date")
    axes[1].xaxis.set_major_locator(mdates.YearLocator(2))
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "price_timeseries.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_returns_distribution(universe: pd.DataFrame):
    """histogram + kde vs normal overlay to visualize fat tails."""
    print("  [4/16] Returns distributions...")

    instruments = ["spy", "qqq", "iwm", "btc_usd"]
    available = [i for i in instruments if i in universe.columns]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    colors = ["#2ecc71", "#3498db", "#9b59b6", "#f39c12"]

    for idx, inst in enumerate(available):
        ax = axes[idx]
        returns = np.log(universe[inst] / universe[inst].shift(1)).dropna()

        ax.hist(returns, bins=100, density=True, alpha=0.6, color=colors[idx], edgecolor="none")
        returns.plot.kde(ax=ax, color=colors[idx], linewidth=2)

        # overlay a normal pdf so fat tails are visually obvious
        mu, sigma = returns.mean(), returns.std()
        x = np.linspace(returns.min(), returns.max(), 200)
        ax.plot(x, stats.norm.pdf(x, mu, sigma), "k--", linewidth=1, alpha=0.7, label="Normal")

        ax.set_title(f"{inst.upper()} Daily Log Returns")
        ax.set_xlabel("Log Return")
        ax.legend([f"KDE (skew={returns.skew():.2f}, kurt={returns.kurtosis():.2f})", "Normal"])
        ax.set_xlim(-0.15, 0.15)

    # hide unused subplot slots
    for idx in range(len(available), 4):
        axes[idx].set_visible(False)

    plt.suptitle("Distribution of Daily Log Returns", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "returns_distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_correlation_heatmap(features: dict):
    """correlation matrix of spy features, capped at top 30 by variance to stay readable."""
    print("  [5/16] Feature correlation heatmap...")

    symbol = "spy"
    if symbol not in features:
        print("       SKIP — no SPY features")
        return

    df = features[symbol].drop(columns=["instrument"], errors="ignore")
    numeric = df.select_dtypes(include=[np.number])

    # too many features makes the heatmap unreadable, keep the most variable ones
    if numeric.shape[1] > 30:
        variances = numeric.var().sort_values(ascending=False)
        top_cols = variances.head(30).index.tolist()
        numeric = numeric[top_cols]

    corr = numeric.corr()

    fig, ax = plt.subplots(figsize=(14, 12))
    # mask upper triangle to avoid redundancy
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr, mask=mask, cmap="RdBu_r", center=0,
        square=True, linewidths=0.5, ax=ax,
        cbar_kws={"shrink": 0.8},
        annot=False,
        fmt=".2f",
        vmin=-1, vmax=1,
    )
    ax.set_title("Feature Correlation Matrix (SPY — Top 30 by Variance)", fontsize=13)
    plt.xticks(fontsize=8, rotation=45, ha="right")
    plt.yticks(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_heatmap.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_cross_asset_correlation(universe: pd.DataFrame):
    """shows how daily returns across asset classes move together."""
    print("  [6/16] Cross-asset correlation...")

    close_cols = ["spy", "qqq", "iwm", "btc_usd", "vix", "xlf", "xlk", "xle", "xlv", "gld", "uso"]
    available = [c for c in close_cols if c in universe.columns]

    returns = np.log(universe[available] / universe[available].shift(1)).dropna()
    corr = returns.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr, cmap="RdBu_r", center=0, annot=True, fmt=".2f",
        square=True, linewidths=1, ax=ax,
        vmin=-1, vmax=1,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Cross-Asset Daily Return Correlations", fontsize=13)
    ax.set_xticklabels([c.upper() for c in available], rotation=45, ha="right")
    ax.set_yticklabels([c.upper() for c in available], rotation=0)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "correlation_cross_asset.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_pca_analysis(features: dict):
    """variance explained curve and 2d projection to check feature redundancy."""
    print("  [7/16] PCA analysis...")

    symbol = "spy"
    if symbol not in features:
        print("       SKIP — no SPY features")
        return

    df = features[symbol].drop(columns=["instrument"], errors="ignore")
    numeric = df.select_dtypes(include=[np.number]).dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(numeric)

    n_components = min(20, X_scaled.shape[1])
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X_scaled)

    cum_var = np.cumsum(pca.explained_variance_ratio_) * 100

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].bar(range(1, n_components + 1), pca.explained_variance_ratio_ * 100,
                alpha=0.7, color="#3498db", label="Individual")
    axes[0].plot(range(1, n_components + 1), cum_var, "r-o", markersize=5, label="Cumulative")
    axes[0].axhline(y=90, color="gray", linestyle="--", alpha=0.7, label="90% threshold")
    # find how many components you actually need for 90% coverage
    n_90 = np.argmax(cum_var >= 90) + 1
    axes[0].axvline(x=n_90, color="green", linestyle="--", alpha=0.7, label=f"{n_90} components for 90%")
    axes[0].set_xlabel("Principal Component")
    axes[0].set_ylabel("Variance Explained (%)")
    axes[0].set_title("PCA — Variance Explained")
    axes[0].legend(fontsize=9)

    # color by time index to spot regime clusters
    scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=range(len(X_pca)),
                              cmap="viridis", alpha=0.3, s=5)
    axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    axes[1].set_title("PCA — 2D Projection (color = time)")
    plt.colorbar(scatter, ax=axes[1], label="Time index")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pca_variance_explained.png", dpi=DPI, bbox_inches="tight")
    plt.close()

    pca_stats = pd.DataFrame({
        "component": range(1, n_components + 1),
        "variance_explained": pca.explained_variance_ratio_,
        "cumulative_variance": cum_var / 100,
    })
    pca_stats.to_csv(METRICS_DIR / "pca_stats.csv", index=False)
    print(f"       {n_90} components needed for 90% variance")


def plot_outlier_analysis(features: dict):
    """box plots for return features and z-score flagging on spy daily returns."""
    print("  [8/16] Outlier analysis...")

    symbol = "spy"
    if symbol not in features:
        return

    df = features[symbol].drop(columns=["instrument"], errors="ignore")

    # grab up to 8 return/momentum columns for the box plot
    return_cols = [c for c in df.columns if "ret" in c or "roc" in c][:8]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    if return_cols:
        df[return_cols].boxplot(ax=axes[0], vert=True, patch_artist=True,
                                 boxprops=dict(facecolor="#3498db", alpha=0.7))
        axes[0].set_title("Box Plots — Return & Momentum Features (SPY)")
        axes[0].tick_params(axis="x", rotation=45)
        axes[0].set_ylabel("Value")

    if "log_ret_1d" in df.columns:
        returns = df["log_ret_1d"]
        z_scores = np.abs(stats.zscore(returns.dropna()))
        outlier_mask = z_scores > 3
        dates = returns.dropna().index

        axes[1].plot(dates, returns.dropna().values, linewidth=0.5, alpha=0.7, color="#3498db")
        axes[1].scatter(dates[outlier_mask], returns.dropna().values[outlier_mask],
                        color="#e74c3c", s=20, zorder=5, label=f"Outliers (|z| > 3): {outlier_mask.sum()}")
        axes[1].set_title("Daily Log Returns with Z-Score Outliers (SPY)")
        axes[1].set_xlabel("Date")
        axes[1].set_ylabel("Log Return")
        axes[1].legend()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "outlier_analysis.png", dpi=DPI, bbox_inches="tight")
    plt.close()

    # save counts at multiple z thresholds so you can pick the right cutoff
    if "log_ret_1d" in df.columns:
        returns = df["log_ret_1d"].dropna()
        z = np.abs(stats.zscore(returns))
        outlier_summary = pd.DataFrame({
            "threshold": [2, 2.5, 3, 3.5],
            "n_outliers": [(z > t).sum() for t in [2, 2.5, 3, 3.5]],
            "pct_outliers": [((z > t).sum() / len(z) * 100).round(2) for t in [2, 2.5, 3, 3.5]],
        })
        outlier_summary.to_csv(METRICS_DIR / "outlier_summary.csv", index=False)
        print(f"       {(z > 3).sum()} outliers at z > 3 threshold")


def plot_rolling_volatility(universe: pd.DataFrame):
    """21-day annualized vol with key market event markers for context."""
    print("  [9/16] Rolling volatility comparison...")

    instruments = ["spy", "qqq", "iwm", "btc_usd"]
    available = [i for i in instruments if i in universe.columns]
    colors = {"spy": "#2ecc71", "qqq": "#3498db", "iwm": "#9b59b6", "btc_usd": "#f39c12"}

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)

    for inst in available:
        returns = np.log(universe[inst] / universe[inst].shift(1))
        # annualize: multiply by sqrt(252 trading days)
        vol = returns.rolling(21).std() * np.sqrt(252) * 100
        ax.plot(vol.index, vol.values, label=inst.upper(), linewidth=1, alpha=0.8,
                color=colors.get(inst))

    # annotate major crisis dates for visual reference
    events = {
        "2008-09-15": "Lehman",
        "2020-03-16": "COVID",
        "2022-06-13": "2022\nBear",
    }
    for date_str, label in events.items():
        try:
            date = pd.Timestamp(date_str)
            if date in universe.index or date > universe.index.min():
                ax.axvline(x=date, color="gray", linestyle=":", alpha=0.5)
                ax.text(date, ax.get_ylim()[1] * 0.95, label, fontsize=8,
                        ha="center", va="top", color="gray")
        except Exception:
            pass

    ax.set_title("21-Day Rolling Annualized Volatility", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility (%)")
    ax.legend(loc="upper right")
    ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rolling_volatility.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_vix_spy_relationship(universe: pd.DataFrame):
    """scatter of vix level vs spy returns, plus dual-axis time series overlay."""
    print("  [10/16] VIX vs SPY relationship...")

    if "vix" not in universe.columns or "spy" not in universe.columns:
        print("       SKIP — VIX or SPY not available")
        return

    spy_ret = np.log(universe["spy"] / universe["spy"].shift(1))
    vix = universe["vix"]
    mask = spy_ret.notna() & vix.notna()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].scatter(vix[mask], spy_ret[mask], alpha=0.1, s=3, color="#3498db")
    axes[0].set_xlabel("VIX Level")
    axes[0].set_ylabel("SPY Daily Log Return")
    axes[0].set_title("VIX Level vs SPY Returns")
    axes[0].axhline(y=0, color="gray", linestyle="--", alpha=0.5)

    ax2 = axes[1]
    ax2.plot(universe.index, universe["spy"] / universe["spy"].dropna().iloc[0] * 100,
             color="#2ecc71", label="SPY (normalized)", linewidth=1)
    ax2_twin = ax2.twinx()
    ax2_twin.plot(universe.index, vix.values, color="#e74c3c", alpha=0.7, linewidth=0.8, label="VIX")
    ax2.set_title("SPY Price vs VIX Level")
    ax2.set_xlabel("Date")
    ax2.set_ylabel("SPY (base=100)", color="#2ecc71")
    ax2_twin.set_ylabel("VIX", color="#e74c3c")
    ax2.legend(loc="upper left")
    ax2_twin.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "vix_spy_relationship.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_yield_curve_vs_market(universe: pd.DataFrame):
    """dual-axis plot highlighting inverted yield curve periods (recession signal)."""
    print("  [11/16] Yield curve vs market...")

    if "yield_spread_10y_2y" not in universe.columns:
        print("       SKIP — yield spread not available")
        return

    fig, ax1 = plt.subplots(figsize=FIGSIZE_WIDE)

    if "spy" in universe.columns:
        ax1.plot(universe.index, universe["spy"], color="#2ecc71", linewidth=1, label="SPY Price")
    ax1.set_ylabel("SPY Price", color="#2ecc71")
    ax1.set_xlabel("Date")

    ax2 = ax1.twinx()
    spread = universe["yield_spread_10y_2y"]
    ax2.plot(universe.index, spread, color="#e74c3c", linewidth=1, alpha=0.8, label="10Y-2Y Spread")
    # shade the inverted (negative spread) regions since they historically precede recessions
    ax2.fill_between(universe.index, 0, spread, where=(spread < 0),
                     color="#e74c3c", alpha=0.2, label="Inverted Yield Curve")
    ax2.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax2.set_ylabel("Yield Spread (%)", color="#e74c3c")

    ax1.set_title("SPY Price vs Treasury Yield Curve Spread (10Y − 2Y)", fontsize=13)
    ax1.legend(loc="upper left")
    ax2.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "yield_curve_vs_market.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_feature_distributions(features: dict):
    """grid of histograms for key engineered features with mean/median markers."""
    print("  [12/16] Feature distribution grid...")

    symbol = "spy"
    if symbol not in features:
        return

    df = features[symbol].drop(columns=["instrument"], errors="ignore")

    key_features = [
        "log_ret_1d", "log_ret_5d", "log_ret_21d",
        "volatility_5d", "volatility_21d", "volatility_63d",
        "rsi_14", "roc_10",
        "dist_sma_21", "dist_sma_200",
        "bollinger_pos", "atr_norm",
    ]
    available = [f for f in key_features if f in df.columns]

    n_cols = 4
    n_rows = (len(available) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3 * n_rows))
    axes = axes.flatten()

    for idx, feat in enumerate(available):
        ax = axes[idx]
        data = df[feat].dropna()
        ax.hist(data, bins=60, density=True, alpha=0.7, color="#3498db", edgecolor="none")
        ax.set_title(feat, fontsize=10)
        ax.tick_params(labelsize=8)

        # red = mean, green = median so you can eyeball skew
        ax.axvline(data.mean(), color="red", linestyle="--", linewidth=1, alpha=0.7)
        ax.axvline(data.median(), color="green", linestyle="--", linewidth=1, alpha=0.7)

    for idx in range(len(available), len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle("Feature Distributions (SPY) — Red=Mean, Green=Median", fontsize=13, y=1.01)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_distributions_grid.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_rsi_comparison(features: dict):
    """overlaid rsi histograms across instruments with overbought/oversold lines."""
    print("  [13/16] RSI comparison...")

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"spy": "#2ecc71", "qqq": "#3498db", "iwm": "#9b59b6", "btc_usd": "#f39c12"}

    for symbol, df in features.items():
        if "rsi_14" in df.columns:
            rsi = df["rsi_14"].dropna()
            ax.hist(rsi, bins=50, density=True, alpha=0.4, label=symbol.upper(),
                    color=colors.get(symbol, "#95a5a6"))

    ax.axvline(30, color="red", linestyle="--", alpha=0.7, label="Oversold (30)")
    ax.axvline(70, color="green", linestyle="--", alpha=0.7, label="Overbought (70)")
    ax.set_title("RSI(14) Distribution by Instrument")
    ax.set_xlabel("RSI")
    ax.set_ylabel("Density")
    ax.legend()

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "rsi_distribution.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_macro_timeseries(universe: pd.DataFrame):
    """stacked subplots for each macro indicator to spot regime shifts."""
    print("  [14/16] Macro time series...")

    macro_cols = {
        "fed_funds_rate": "Fed Funds Rate (%)",
        "treasury_10y": "10Y Treasury (%)",
        "unemployment": "Unemployment (%)",
        "cpi": "CPI Index",
    }
    available = {k: v for k, v in macro_cols.items() if k in universe.columns}

    if not available:
        print("       SKIP — no macro data")
        return

    n = len(available)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3 * n), sharex=True)
    if n == 1:
        axes = [axes]

    for idx, (col, label) in enumerate(available.items()):
        axes[idx].plot(universe.index, universe[col], linewidth=1, color="#3498db")
        axes[idx].set_ylabel(label, fontsize=10)
        axes[idx].set_title(label, fontsize=11)

    axes[-1].set_xlabel("Date")
    plt.suptitle("Macroeconomic Indicators", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "macro_timeseries.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_sector_comparison(universe: pd.DataFrame):
    """normalized performance chart for sector etfs on a log scale."""
    print("  [15/16] Sector ETF comparison...")

    sectors = ["xlf", "xlk", "xle", "xlv"]
    available = [s for s in sectors if s in universe.columns]

    if not available:
        print("       SKIP — no sector data")
        return

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    colors = ["#e74c3c", "#3498db", "#f39c12", "#2ecc71"]

    for idx, sector in enumerate(available):
        series = universe[sector].dropna()
        normalized = series / series.iloc[0] * 100
        ax.plot(normalized.index, normalized.values, label=sector.upper(),
                linewidth=1.2, color=colors[idx % len(colors)])

    ax.set_title("Sector ETF Performance (Normalized)", fontsize=13)
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalized (base=100)")
    ax.legend()
    ax.set_yscale("log")

    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "sector_comparison.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def generate_data_quality_report(universe: pd.DataFrame, features: dict):
    """writes a plain-text quality summary covering shape, date range, and missingness."""
    print("  [16/20] Data quality report...")

    lines = []
    lines.append("AEGIS V1 — Data Quality Report")
    lines.append("=" * 50)
    lines.append(f"\nUniverse: {universe.shape[0]} rows × {universe.shape[1]} columns")
    lines.append(f"Date range: {universe.index.min().date()} → {universe.index.max().date()}")
    lines.append(f"Total missing values: {universe.isnull().sum().sum()}")
    lines.append(f"Missing after forward-fill: {universe.isnull().sum().sum()}")

    lines.append(f"\n--- Feature Datasets ---")
    for symbol, df in features.items():
        n_feat = len([c for c in df.columns if c != "instrument"])
        lines.append(f"  {symbol}: {n_feat} features × {len(df)} rows")
        missing = df.isnull().sum().sum()
        lines.append(f"    Missing: {missing} ({missing / df.size * 100:.4f}%)")

    report = "\n".join(lines)
    path = METRICS_DIR / "data_quality_report.txt"
    with open(path, "w") as f:
        f.write(report)
    print(f"       Saved → {path}")
    print(report)


def plot_cleaning_before_after(universe: pd.DataFrame):
    """compares raw vs cleaned data side-by-side using saved snapshots from build_dataset."""
    print("  [17/20] Cleaning before/after visualization...")

    raw_path = PROCESSED_DIR / "universe_raw_snapshot.parquet"
    log_path = PROCESSED_DIR / "cleaning_log.json"
    missing_report_path = PROCESSED_DIR / "missing_value_report.csv"

    if not raw_path.exists():
        print("       SKIP — raw snapshot not found (re-run build_dataset.py)")
        return

    import json
    raw = pd.read_parquet(raw_path)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # top left: raw missing values before any cleaning
    raw_missing = raw.isnull().sum().sort_values(ascending=False)
    raw_missing_pct = (raw_missing / len(raw) * 100)
    top_missing = raw_missing_pct[raw_missing_pct > 0].head(15)

    if len(top_missing) > 0:
        axes[0, 0].barh(range(len(top_missing)), top_missing.values, color="#e74c3c", alpha=0.8)
        axes[0, 0].set_yticks(range(len(top_missing)))
        axes[0, 0].set_yticklabels(top_missing.index, fontsize=9)
        axes[0, 0].set_xlabel("Missing (%)")
        axes[0, 0].set_title("BEFORE Cleaning — Missing Values (Top 15)", fontweight="bold")
        axes[0, 0].invert_yaxis()
    else:
        axes[0, 0].text(0.5, 0.5, "No missing values in raw data", ha="center", va="center")
        axes[0, 0].set_title("BEFORE Cleaning", fontweight="bold")

    # top right: what's left after cleaning
    clean_missing = universe.isnull().sum().sort_values(ascending=False)
    clean_missing_pct = (clean_missing / len(universe) * 100)
    top_clean = clean_missing_pct[clean_missing_pct > 0].head(15)

    if len(top_clean) > 0:
        axes[0, 1].barh(range(len(top_clean)), top_clean.values, color="#2ecc71", alpha=0.8)
        axes[0, 1].set_yticks(range(len(top_clean)))
        axes[0, 1].set_yticklabels(top_clean.index, fontsize=9)
        axes[0, 1].set_xlabel("Missing (%)")
        axes[0, 1].set_title("AFTER Cleaning — Missing Values (Top 15)", fontweight="bold")
        axes[0, 1].invert_yaxis()
    else:
        axes[0, 1].text(0.5, 0.5, "All missing values resolved!", ha="center", va="center", fontsize=13, color="#2ecc71")
        axes[0, 1].set_title("AFTER Cleaning", fontweight="bold")

    # bottom left: row counts at each cleaning step
    if log_path.exists():
        with open(log_path) as f:
            cleaning_log = json.load(f)

        steps_with_rows = [s for s in cleaning_log if "rows_before" in s and "rows_after" in s]
        if steps_with_rows:
            step_labels = [f"Step {s['step']}: {s['action'][:30]}" for s in steps_with_rows]
            before_vals = [s["rows_before"] for s in steps_with_rows]
            after_vals = [s["rows_after"] for s in steps_with_rows]

            x = range(len(step_labels))
            width = 0.35
            axes[1, 0].bar([i - width/2 for i in x], before_vals, width, label="Before", color="#e74c3c", alpha=0.7)
            axes[1, 0].bar([i + width/2 for i in x], after_vals, width, label="After", color="#2ecc71", alpha=0.7)
            axes[1, 0].set_xticks(list(x))
            axes[1, 0].set_xticklabels(step_labels, rotation=30, ha="right", fontsize=8)
            axes[1, 0].set_ylabel("Row Count")
            axes[1, 0].set_title("Rows Before/After Each Cleaning Step", fontweight="bold")
            axes[1, 0].legend()
    else:
        axes[1, 0].text(0.5, 0.5, "Cleaning log not found", ha="center", va="center")

    # bottom right: per-column missing counts before vs after
    if missing_report_path.exists():
        mr = pd.read_csv(missing_report_path)
        mr = mr[mr["missing_before_cleaning"] > 0].sort_values("missing_before_cleaning", ascending=False).head(12)
        if len(mr) > 0:
            x = range(len(mr))
            width = 0.35
            axes[1, 1].bar([i - width/2 for i in x], mr["missing_before_cleaning"], width,
                           label="Before", color="#e74c3c", alpha=0.7)
            axes[1, 1].bar([i + width/2 for i in x], mr["missing_after_cleaning"], width,
                           label="After", color="#2ecc71", alpha=0.7)
            axes[1, 1].set_xticks(list(x))
            axes[1, 1].set_xticklabels(mr["column"], rotation=45, ha="right", fontsize=8)
            axes[1, 1].set_ylabel("Missing Count")
            axes[1, 1].set_title("Per-Column Missing: Before vs After", fontweight="bold")
            axes[1, 1].legend()
    else:
        axes[1, 1].text(0.5, 0.5, "Missing report not found", ha="center", va="center")

    plt.suptitle("Data Cleaning Process — Before vs After", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "cleaning_before_after.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_transformation_examples(universe: pd.DataFrame):
    """shows raw price vs log returns vs rolling vol to illustrate feature engineering."""
    print("  [18/20] Data transformation examples...")

    if "spy" not in universe.columns:
        print("       SKIP — SPY not available")
        return

    fig, axes = plt.subplots(3, 2, figsize=(16, 14))

    spy = universe["spy"].dropna()

    # left column: raw data, right column: transformed version
    axes[0, 0].plot(spy.index, spy.values, linewidth=0.8, color="#3498db")
    axes[0, 0].set_title("Raw: SPY Close Price", fontweight="bold")
    axes[0, 0].set_ylabel("Price ($)")

    log_ret = np.log(spy / spy.shift(1)).dropna()
    axes[0, 1].plot(log_ret.index, log_ret.values, linewidth=0.4, color="#2ecc71", alpha=0.8)
    axes[0, 1].set_title("Transformed: Log Returns (stationary)", fontweight="bold")
    axes[0, 1].set_ylabel("Log Return")
    axes[0, 1].axhline(0, color="gray", linestyle="--", alpha=0.5)

    axes[1, 0].plot(spy.index, spy.values, linewidth=0.8, color="#3498db")
    axes[1, 0].set_title("Raw: SPY Close Price", fontweight="bold")
    axes[1, 0].set_ylabel("Price ($)")

    vol_21 = log_ret.rolling(21).std() * np.sqrt(252) * 100
    axes[1, 1].plot(vol_21.index, vol_21.values, linewidth=1, color="#e74c3c")
    axes[1, 1].set_title("Transformed: 21-Day Rolling Volatility (%)", fontweight="bold")
    axes[1, 1].set_ylabel("Annualized Vol (%)")
    axes[1, 1].set_ylim(bottom=0)

    if "spy_volume" in universe.columns:
        vol = universe["spy_volume"].dropna()
        axes[2, 0].plot(vol.index, vol.values, linewidth=0.3, color="#9b59b6", alpha=0.7)
        axes[2, 0].set_title("Raw: SPY Volume", fontweight="bold")
        axes[2, 0].set_ylabel("Volume")

        # ratio to moving average normalizes volume across different market periods
        vol_ma = vol.rolling(20).mean()
        vol_ratio = (vol / vol_ma).dropna()
        axes[2, 1].plot(vol_ratio.index, vol_ratio.values, linewidth=0.4, color="#f39c12", alpha=0.8)
        axes[2, 1].axhline(1, color="gray", linestyle="--", alpha=0.5)
        axes[2, 1].set_title("Transformed: Volume / 20-Day MA (normalized)", fontweight="bold")
        axes[2, 1].set_ylabel("Volume Ratio")
    else:
        axes[2, 0].text(0.5, 0.5, "Volume not available", ha="center", va="center")
        axes[2, 1].text(0.5, 0.5, "Volume not available", ha="center", va="center")

    for ax in axes.flatten():
        ax.set_xlabel("Date")

    plt.suptitle("Data Transformations: Raw → Engineered Features", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "transformation_examples.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def plot_target_variable_exploration(universe: pd.DataFrame):
    """forward return distributions, class balance, autocorrelation, and rolling sharpe."""
    print("  [19/20] Target variable exploration...")

    if "spy" not in universe.columns:
        print("       SKIP — SPY not available")
        return

    spy = universe["spy"]

    # compute forward-looking returns at multiple horizons (these are labels, not features)
    horizons = {"1d": 1, "5d": 5, "10d": 10, "21d": 21}
    fwd_returns = {}
    for label, h in horizons.items():
        fwd_returns[label] = np.log(spy.shift(-h) / spy)  # Forward-looking (label, not feature)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # top left: overlaid histograms for each horizon
    ax = axes[0, 0]
    for label, ret in fwd_returns.items():
        ret.dropna().hist(bins=80, density=True, alpha=0.4, ax=ax, label=label)
    ax.set_title("Forward Return Distribution (SPY)")
    ax.set_xlabel("Forward Log Return")
    ax.set_ylabel("Density")
    ax.legend()
    ax.axvline(0, color="black", linestyle="--", alpha=0.5)

    # top right: up/down class balance (matters for classification framing)
    ax = axes[0, 1]
    class_balance = {}
    for label, ret in fwd_returns.items():
        r = ret.dropna()
        up_pct = (r > 0).mean() * 100
        class_balance[label] = {"Up": up_pct, "Down": 100 - up_pct}

    labels = list(class_balance.keys())
    ups = [class_balance[l]["Up"] for l in labels]
    downs = [class_balance[l]["Down"] for l in labels]
    x = range(len(labels))
    ax.bar(x, ups, color="#2ecc71", alpha=0.7, label="Up (positive return)")
    ax.bar(x, downs, bottom=ups, color="#e74c3c", alpha=0.7, label="Down (negative return)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Class Balance: Up vs Down by Horizon")
    ax.legend()
    ax.axhline(50, color="gray", linestyle="--", alpha=0.5)

    # bottom left: autocorrelation to check if returns are predictable
    ax = axes[1, 0]
    ret_1d = np.log(spy / spy.shift(1)).dropna()
    max_lags = 30
    autocorrs = [ret_1d.autocorr(lag=i) for i in range(1, max_lags + 1)]
    ax.bar(range(1, max_lags + 1), autocorrs, color="#3498db", alpha=0.7)
    ax.axhline(0, color="gray", linestyle="--")
    # approximate 95% confidence band
    n = len(ret_1d)
    ax.axhline(1.96 / np.sqrt(n), color="red", linestyle=":", alpha=0.7, label="95% CI")
    ax.axhline(-1.96 / np.sqrt(n), color="red", linestyle=":", alpha=0.7)
    ax.set_xlabel("Lag (days)")
    ax.set_ylabel("Autocorrelation")
    ax.set_title("Return Autocorrelation (SPY) — Predictability Check")
    ax.legend()

    # bottom right: rolling sharpe as a quick regime indicator
    ax = axes[1, 1]
    rolling_mean = ret_1d.rolling(63).mean() * 252
    rolling_std = ret_1d.rolling(63).std() * np.sqrt(252)
    rolling_sharpe = rolling_mean / rolling_std
    ax.plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=0.8, color="#9b59b6")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(1, color="green", linestyle=":", alpha=0.5, label="Sharpe = 1")
    ax.axhline(-1, color="red", linestyle=":", alpha=0.5, label="Sharpe = -1")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rolling Sharpe (63d)")
    ax.set_title("Rolling Sharpe Ratio — Market Regime Proxy")
    ax.legend()
    ax.set_ylim(-5, 5)

    plt.suptitle("Target Variable Analysis: Forward Returns", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "target_variable_exploration.png", dpi=DPI, bbox_inches="tight")
    plt.close()

    target_stats = {}
    for label, ret in fwd_returns.items():
        r = ret.dropna()
        target_stats[label] = {
            "mean": r.mean(),
            "std": r.std(),
            "skew": r.skew(),
            "kurtosis": r.kurtosis(),
            "pct_positive": (r > 0).mean(),
            "min": r.min(),
            "max": r.max(),
            "sharpe_approx": r.mean() / r.std() * np.sqrt(252 / int(label.replace("d", ""))),
        }
    pd.DataFrame(target_stats).T.to_csv(METRICS_DIR / "target_variable_stats.csv")
    print("       Saved target_variable_stats.csv")


def plot_stationarity_check(universe: pd.DataFrame):
    """rolling mean/variance comparison showing why we transform prices to returns."""
    print("  [20/20] Stationarity check...")

    if "spy" not in universe.columns:
        return

    spy = universe["spy"].dropna()
    ret = np.log(spy / spy.shift(1)).dropna()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    window = 252
    # top row: raw price has a drifting mean and growing variance (non-stationary)
    axes[0, 0].plot(spy.index, spy.values, linewidth=0.8, color="#3498db", alpha=0.8)
    axes[0, 0].plot(spy.rolling(window).mean().index, spy.rolling(window).mean().values,
                     color="red", linewidth=2, label=f"Rolling mean ({window}d)")
    axes[0, 0].set_title("SPY Price — Non-Stationary", fontweight="bold")
    axes[0, 0].set_ylabel("Price")
    axes[0, 0].legend()

    axes[0, 1].plot(spy.rolling(window).var().index, spy.rolling(window).var().values,
                     color="#e74c3c", linewidth=1)
    axes[0, 1].set_title("SPY Price — Rolling Variance (non-constant)", fontweight="bold")
    axes[0, 1].set_ylabel("Variance")

    # bottom row: log returns have a stable mean near zero and bounded variance
    axes[1, 0].plot(ret.index, ret.values, linewidth=0.3, color="#2ecc71", alpha=0.7)
    axes[1, 0].plot(ret.rolling(window).mean().index, ret.rolling(window).mean().values,
                     color="red", linewidth=2, label=f"Rolling mean ({window}d)")
    axes[1, 0].set_title("SPY Log Returns — Approximately Stationary", fontweight="bold")
    axes[1, 0].set_ylabel("Log Return")
    axes[1, 0].axhline(0, color="gray", linestyle="--", alpha=0.5)
    axes[1, 0].legend()

    axes[1, 1].plot(ret.rolling(window).var().index, ret.rolling(window).var().values,
                     color="#e74c3c", linewidth=1)
    axes[1, 1].set_title("SPY Returns — Rolling Variance (more stable)", fontweight="bold")
    axes[1, 1].set_ylabel("Variance")

    for ax in axes.flatten():
        ax.set_xlabel("Date")

    plt.suptitle("Stationarity: Why We Transform Prices → Returns", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "stationarity_check.png", dpi=DPI, bbox_inches="tight")
    plt.close()


def main():
    """runs all 20 eda steps in sequence and prints output locations."""
    print("\n🏛️  AEGIS V1 — Exploratory Data Analysis")
    print("=" * 60)

    universe, features = load_data()
    print(f"Loaded universe: {universe.shape}")
    print(f"Loaded features for: {list(features.keys())}")

    generate_summary_statistics(universe)
    plot_missing_values(universe)
    plot_price_timeseries(universe)
    plot_returns_distribution(universe)
    plot_correlation_heatmap(features)
    plot_cross_asset_correlation(universe)
    plot_pca_analysis(features)
    plot_outlier_analysis(features)
    plot_rolling_volatility(universe)
    plot_vix_spy_relationship(universe)
    plot_yield_curve_vs_market(universe)
    plot_feature_distributions(features)
    plot_rsi_comparison(features)
    plot_macro_timeseries(universe)
    plot_sector_comparison(universe)
    generate_data_quality_report(universe, features)
    plot_cleaning_before_after(universe)
    plot_transformation_examples(universe)
    plot_target_variable_exploration(universe)
    plot_stationarity_check(universe)

    print("\n" + "=" * 60)
    print("EDA COMPLETE")
    print("=" * 60)
    print(f"  Figures: {FIGURES_DIR}")
    print(f"  Metrics: {METRICS_DIR}")
    print(f"  Total figures: {len(list(FIGURES_DIR.glob('*.png')))}")


if __name__ == "__main__":
    main()

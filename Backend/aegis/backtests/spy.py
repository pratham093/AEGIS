"""SPY backtest — GMM regime + base rule."""

from aegis.backtests.core import *

# spy uses gmm with 2 regimes; ema smoothing prevents whipsaw on exits
CONFIG = AssetConfig(
    name="SPY", close_col="spy",
    regime_type="gmm", regime_k=2,
    use_base_rule=True,
    top_n_features=15,
    risk_target_vol=0.15,
    risk_max_exposure=1.0,
    risk_regime_crisis_cap=0.5,
    exposure_ema_halflife=5,
)


def run_spy_backtest():
    """run the full spy backtest pipeline and return result dict."""
    print("\n  SPY backtest starting...")

    # load price universe, asset-specific features, and cross-asset signals
    universe = load_universe()
    features = load_features(CONFIG.close_col)
    xf = build_cross_asset_features(universe)

    df_sig, asset_close, asset_returns, regime_in_sig = prepare_asset_data(
        CONFIG, features, universe, xf
    )
    print(f"  Data: {df_sig.shape[0]} rows, {df_sig.shape[1]} features")

    # generate binary long/flat signal from the base rule
    signals = base_rule(df_sig, universe, "SPY")
    long_pct = signals.mean() * 100
    print(f"  Base rule: LONG {long_pct:.1f}% of days ({int(signals.sum())} / {len(signals)})")

    # fit gmm on regime features to classify market states
    r_input = [c for c in regime_in_sig if c in df_sig.columns]
    rdata = df_sig[r_input].dropna()
    sc = StandardScaler()
    X_regime = sc.fit_transform(rdata)
    labels, probs, _ = fit_regime(X_regime, CONFIG.regime_type, CONFIG.regime_k)

    # orient so higher label = higher vol (crisis), keeps interpretation consistent
    labels, probs = orient_regime_labels(
        labels, probs, df_sig.loc[rdata.index, "volatility_21d"].values, CONFIG.regime_k
    )

    regime_series = pd.Series(labels, index=rdata.index)
    conf_series = pd.Series(np.max(probs, axis=1), index=rdata.index)

    # walk through each day and let the risk engine size the position
    results = []
    for date in df_sig.index:
        sig = float(signals.get(date, 0))
        rl = int(regime_series.get(date, 1))
        rc = float(conf_series.get(date, 0.5))
        rv = float(df_sig.loc[date, "realized_vol_21d"])
        # trailing 1y window gives the risk engine enough history for vol scaling
        ret_hist = asset_returns.loc[:date].tail(252)

        risk = risk_engine_v2(sig, sig, rl, rc, rv, ret_hist, CONFIG)
        risk.update({"date": date, "signal_prob": sig,
                     "asset_ret": float(asset_returns.get(date, 0)),
                     "regime_label": rl})
        results.append(risk)

    result = compute_backtest_metrics("SPY", CONFIG, results, asset_returns)
    plot_single_asset("SPY", result, color="#2ecc71")
    save_asset_outputs("SPY", result)
    return result


if __name__ == "__main__":
    run_spy_backtest()

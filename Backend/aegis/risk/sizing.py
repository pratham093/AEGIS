"""Position sizing — conviction + risk caps + smoothing."""
import numpy as np
import pandas as pd


def compute_conviction(prob, tau):
    return np.clip((prob - tau) / (1.0 - tau), 0.0, 1.0)


def compute_vol_cap(realized_vol, target_vol):
    if realized_vol <= 0 or np.isnan(realized_vol):
        return 1.0
    return np.clip(target_vol / realized_vol, 0.0, 2.0)


def compute_var_cap(var_95, loss_budget):
    if var_95 >= 0 or np.isnan(var_95):
        return 1.0
    return np.clip(loss_budget / abs(var_95), 0.0, 1.5)


def compute_regime_cap(p_crisis):
    cap = 1.0 - 0.65 * p_crisis
    return np.clip(cap, 0.20, 1.0)


def compute_dd_cap(drawdown):
    if drawdown < -0.15:
        return 0.25
    elif drawdown < -0.10:
        return 0.50
    elif drawdown < -0.05:
        return 0.75
    return 1.0


def size_position(prob, tau, realized_vol, target_vol,
                  var_95, loss_budget, p_crisis, drawdown,
                  prev_exposure=0.0, smoothing=0.3,
                  min_exposure_for_strong=0.15, strong_threshold=0.68):
    flags = []

    conviction = compute_conviction(prob, tau)
    if conviction == 0:
        flags.append('BELOW_THRESHOLD')

    desired_exposure = conviction

    vol_cap = compute_vol_cap(realized_vol, target_vol)
    var_cap = compute_var_cap(var_95, loss_budget)
    regime_cap = compute_regime_cap(p_crisis)
    dd_cap = compute_dd_cap(drawdown)

    hard_cap = min(vol_cap, var_cap, regime_cap, dd_cap, 1.0)

    raw_exposure = min(desired_exposure, hard_cap)

    # floor for strong signals
    if prob > strong_threshold and raw_exposure < min_exposure_for_strong:
        raw_exposure = min_exposure_for_strong
        flags.append('FLOOR_APPLIED')

    if realized_vol > 0.30:
        flags.append('HIGH_VOL')
    if p_crisis > 0.6:
        flags.append('CRISIS_REGIME')
    if drawdown < -0.05:
        flags.append('DRAWDOWN_GUARD')
    if prob < tau:
        flags.append('LOW_CONFIDENCE')

    exposure = (1 - smoothing) * prev_exposure + smoothing * raw_exposure
    exposure = np.clip(exposure, 0.0, 1.0)

    risk_score = int(np.clip(
        (realized_vol / 0.30) * 25 +
        p_crisis * 25 +
        (1 - prob) * 25 +
        abs(min(0, drawdown)) * 167,
        0, 100
    ))

    return {
        'exposure': round(exposure, 4),
        'risk_score': risk_score,
        'flags': flags,
        'conviction': round(conviction, 4),
        'desired_exposure': round(desired_exposure, 4),
        'vol_cap': round(vol_cap, 4),
        'var_cap': round(var_cap, 4),
        'regime_cap': round(regime_cap, 4),
        'dd_cap': round(dd_cap, 4),
        'hard_cap': round(hard_cap, 4),
        'var_95': round(var_95, 6) if not np.isnan(var_95) else None,
    }


ASSET_CONFIGS = {
    'SPY':  {'target_vol': 0.12, 'loss_budget': 0.01, 'tau': 0.60},
    'QQQ':  {'target_vol': 0.14, 'loss_budget': 0.01, 'tau': 0.65},
    'IWM':  {'target_vol': 0.14, 'loss_budget': 0.01, 'tau': 0.70},
    'BTC':  {'target_vol': 0.30, 'loss_budget': 0.02, 'tau': 0.65},
    'GLD':  {'target_vol': 0.10, 'loss_budget': 0.01, 'tau': 0.60},
}


def backtest_with_sizing(strat_df, asset_name, regime_labels, regime_probs,
                         smoothing=0.3):
    cfg = ASSET_CONFIGS.get(asset_name, ASSET_CONFIGS['SPY'])
    tau = cfg['tau']
    target_vol = cfg['target_vol']
    loss_budget = cfg['loss_budget']
    
    results = []
    prev_exp = 0.0
    cum_ret = 0.0
    peak = 0.0
    
    for i, (date, row) in enumerate(strat_df.iterrows()):
        rv = strat_df['ret'].iloc[max(0, i-21):i].std() * np.sqrt(252) if i > 21 else 0.15
        hist = strat_df['ret'].iloc[max(0, i-252):i]
        var95 = hist.quantile(0.05) if len(hist) > 60 else -0.02
        rl = regime_labels[i] if i < len(regime_labels) else 1
        p_crisis = regime_probs[i][0] if i < len(regime_probs) else 0.3  # prob of regime 0

        cum_ret += row.get('ret', 0)
        peak = max(peak, cum_ret)
        dd = cum_ret - peak

        out = size_position(
            prob=row['prob'], tau=tau,
            realized_vol=rv, target_vol=target_vol,
            var_95=var95, loss_budget=loss_budget,
            p_crisis=p_crisis, drawdown=dd,
            prev_exposure=prev_exp, smoothing=smoothing,
        )
        prev_exp = out['exposure']
        
        out['date'] = date
        out['prob'] = row['prob']
        out['actual'] = row['actual']
        out['asset_ret'] = row['ret']
        out['sized_ret'] = out['exposure'] * row['ret']
        results.append(out)
    
    rdf = pd.DataFrame(results).set_index('date')
    rdf['cum_sized'] = rdf['sized_ret'].cumsum()
    rdf['cum_bh'] = rdf['asset_ret'].cumsum()
    
    return rdf

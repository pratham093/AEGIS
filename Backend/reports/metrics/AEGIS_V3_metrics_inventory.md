# AEGIS_V3 Metrics Inventory

Generated: 2026-03-12T13:17:57
Project root: `/Users/prathamshah/Desktop/CODE/AEGIS_V3/Backend`

## Metric Artifacts By Folder

### `app/reports/metrics`
- `app/reports/metrics/data_quality_report.txt`
- `app/reports/metrics/feature_importance.csv`
- `app/reports/metrics/missing_values_summary.csv`
- `app/reports/metrics/pca_stats.csv`
- `app/reports/metrics/regime_conditional_performance.csv`
- `app/reports/metrics/regime_model_comparison.csv`
- `app/reports/metrics/signal_model_comparison.csv`
- `app/reports/metrics/summary_statistics.csv`
- `app/reports/metrics/target_variable_stats.csv`

### `app/data/processed`
- `app/data/processed/cleaning_log.json`
- `app/data/processed/missing_value_report.csv`
- `app/data/processed/outlier_flags.parquet`
- `app/data/processed/regime_assignments.parquet`
- `app/data/processed/universe.parquet`
- `app/data/processed/universe_raw_snapshot.parquet`

### `app/models`
- `app/models/regime/gmm_final.pkl`
- `app/models/regime/scaler_regime.pkl`
- `app/models/selection_metadata.json`
- `app/models/signal/lgbm_final.pkl`
- `app/models/signal/logistic_regression_final.pkl`
- `app/models/signal/scaler_signal.pkl`

### `app/pipelines`
- `app/pipelines/.DS_Store`
- `app/pipelines/__init__.py`
- `app/pipelines/__pycache__/eda.cpython-311.pyc`
- `app/pipelines/__pycache__/feature_engineering.cpython-311.pyc`
- `app/pipelines/build_dataset.py`
- `app/pipelines/eda.py`
- `app/pipelines/feature_engineering.py`

### `app/data`
- `app/data/.DS_Store`
- `app/data/AEGIS_Model_Exploration.ipynb`
- `app/data/AEGIS_Model_Exploration_V2.ipynb`
- `app/data/features/features_all.parquet`
- `app/data/features/features_btc_usd.parquet`
- `app/data/features/features_iwm.parquet`
- `app/data/features/features_qqq.parquet`
- `app/data/features/features_spy.parquet`
- `app/data/processed/cleaning_log.json`
- `app/data/processed/missing_value_report.csv`
- `app/data/processed/outlier_flags.parquet`
- `app/data/processed/regime_assignments.parquet`
- `app/data/processed/universe.parquet`
- `app/data/processed/universe_raw_snapshot.parquet`
- `app/data/raw/fama_french.parquet`
- `app/data/raw/fred_macro.parquet`
- `app/data/raw/ohlcv_btc_usd.parquet`
- `app/data/raw/ohlcv_gld.parquet`
- `app/data/raw/ohlcv_iwm.parquet`
- `app/data/raw/ohlcv_qqq.parquet`
- `app/data/raw/ohlcv_spy.parquet`
- `app/data/raw/ohlcv_uso.parquet`
- `app/data/raw/ohlcv_vix.parquet`
- `app/data/raw/ohlcv_xle.parquet`
- `app/data/raw/ohlcv_xlf.parquet`
- `app/data/raw/ohlcv_xlk.parquet`
- `app/data/raw/ohlcv_xlv.parquet`

## CSV Metrics (Full Contents)

### `app/reports/metrics/feature_importance.csv`
- Shape: `27 rows x 2 cols`
```csv
feature,importance
dist_sma_50,76
dist_sma_200,69
unemployment,67
ff_smb,52
yield_spread_10y_2y,51
volatility_21d,49
bollinger_pos,36
rsi_14,36
volatility_10d,34
atr_14,33
vix,33
ff_hml,32
regime_prob_0,21
dist_sma_21,20
atr_norm,20
dist_sma_10,17
volume_ratio_20d,17
ff_mkt_rf,15
regime_prob_1,13
log_ret_5d,13
vix_change_1d,12
volume_change,11
roc_10,7
ff_rf,6
ma_cross_10_50,1
log_ret_1d,1
regime_label,0
```

### `app/reports/metrics/missing_values_summary.csv`
- Shape: `4 rows x 3 cols`
```csv
Unnamed: 0,count,percent
ff_mkt_rf,44,1.05
ff_smb,44,1.05
ff_hml,44,1.05
ff_rf,44,1.05
```

### `app/reports/metrics/pca_stats.csv`
- Shape: `20 rows x 3 cols`
```csv
component,variance_explained,cumulative_variance
1,0.3060302452238668,0.3060302452238668
2,0.1680856692712375,0.4741159144951044
3,0.1502781199923615,0.6243940344874659
4,0.0729687775008585,0.6973628119883244
5,0.0466746282478584,0.7440374402361827
6,0.0290772672346016,0.7731147074707845
7,0.0275037825515229,0.8006184900223074
8,0.0244278067389879,0.8250462967612955
9,0.0229850800711772,0.8480313768324728
10,0.0216303238255735,0.8696617006580462
11,0.0179419243180571,0.8876036249761031
12,0.0133631006237903,0.9009667255998935
13,0.012449335661692,0.9134160612615856
14,0.0109710291206613,0.9243870903822468
15,0.0098428259317543,0.9342299163140012
16,0.0087903058133962,0.9430202221273974
17,0.0077883729261489,0.9508085950535464
18,0.0075584589967984,0.958367054050345
19,0.0062521308189547,0.9646191848692997
20,0.0059019485171041,0.9705211333864038
```

### `app/reports/metrics/regime_conditional_performance.csv`
- Shape: `2 rows x 5 cols`
```csv
Regime,N,Accuracy,F1,AUC
Crisis/High-Vol,92,0.6630434782608695,0.7737226277372263,0.6901041666666667
Neutral,136,0.6838235294117647,0.7922705314009661,0.68
```

### `app/reports/metrics/regime_model_comparison.csv`
- Shape: `5 rows x 4 cols`
```csv
Metric,GMM,HMM,Winner
Silhouette,0.3400,0.2507,GMM
Davies-Bouldin,1.4875,1.6978,GMM
Calinski-Harabasz,1343.02,1009.22,GMM
Stability (ARI),1.0000,0.9107,GMM
Regime Persistence,No,Yes,HMM
```

### `app/reports/metrics/signal_model_comparison.csv`
- Shape: `4 rows x 6 cols`
```csv
Model,Accuracy,Precision,Recall,F1,AUC-ROC
LightGBM,0.5693 ± 0.0858,0.601,0.7943,0.6762,0.5130 ± 0.1089
XGBoost,0.5702 ± 0.0723,0.592,0.9038,0.7093,0.4861 ± 0.0600
Random Forest,0.5877 ± 0.0816,0.5897,0.9872,0.7352,0.4987 ± 0.0510
Logistic Regression,0.5719 ± 0.0747,0.5857,0.9428,0.7181,0.4938 ± 0.0714
```

### `app/reports/metrics/summary_statistics.csv`
- Shape: `38 rows x 13 cols`
```csv
Unnamed: 0,count,mean,std,min,25%,50%,75%,max,missing,missing_pct,skewness,kurtosis
spy,4173.0,337.7833176664731,145.85117351430682,153.83006286621094,213.29864501953125,297.0732421875,424.3563232421875,695.489990234375,0,0.0,0.6992162988864298,-0.5091049145325952
qqq,4173.0,264.6828144566207,149.23919165434606,84.20404815673828,134.83914184570312,227.8520050048828,360.8048400878906,634.9519653320312,0,0.0,0.6877018966761854,-0.5645029546495217
iwm,4173.0,159.1981042148454,43.484586698320726,83.26619720458984,123.19456481933594,152.05690002441406,196.92291259765625,269.7900085449219,0,0.0,0.2737040795543956,-0.9485301376560722
btc_usd,4173.0,27506.91265054461,32059.59033509928,178.10299682617188,2805.6201171875,10975.599609375,43023.97265625,124752.53125,0,0.0,1.276739544181572,0.5956577354250783
vix,4173.0,18.166899128494975,6.9541688841309774,9.140000343322754,13.489999771118164,16.3799991607666,20.969999313354492,82.69000244140625,0,0.0,2.560372735759906,12.544632939470556
xlf,4173.0,28.799452862121377,10.984321830802326,13.257007598876951,20.487218856811523,25.123613357543945,34.934410095214844,56.400001525878906,0,0.0,0.7360242513460886,-0.3574764935587509
xlk,4173.0,57.67103068582337,35.99458522734872,16.240995407104492,26.202566146850582,48.305023193359375,80.55583190917969,151.83470153808594,0,0.0,0.7413826416235102,-0.4838219397014138
xle,4173.0,28.756031260340727,9.433580171273668,9.305682182312012,22.454326629638672,24.814647674560547,38.72191619873047,54.97999954223633,0,0.0,0.4732780212604598,-0.9430076767502382
xlv,4173.0,98.57250744188656,31.413451733624782,50.0780143737793,68.88532257080078,93.2936019897461,126.7427749633789,159.66000366210938,0,0.0,0.1466924820040016,-1.4546921122498797
gld,4173.0,167.69972670349662,66.48134064683387,100.5,120.41999816894533,158.00999450683594,181.0800018310547,495.8999938964844,0,0.0,1.9799890231957984,4.275364216039726
uso,4173.0,83.81059418574758,36.01922026269662,17.040000915527344,68.69000244140625,78.0,93.76000213623048,284.1600036621094,0,0.0,2.002089667607639,7.392062916912697
spy_open,4173.0,337.7171932325107,145.81285219217813,151.1790964021051,213.56075494675216,297.13805552103923,424.0351838301639,697.0499877929688,0,0.0,0.7002360468525276,-0.506244591529549
spy_high,4173.0,339.5345414683028,146.52600052581104,154.91191717539053,214.60054051573684,298.6379863970685,426.22968653702213,697.8400268554688,0,0.0,0.6950023890992572,-0.5168839112242121
spy_low,4173.0,335.73656670814665,145.0308146503715,150.23767911906552,212.7394663393128,295.5641707964814,421.5086210577569,693.9400024414062,0,0.0,0.7046238038354593,-0.4991217789372393
spy_volume,4173.0,89672194.72801343,45945371.02743662,20270000.0,60846800.0,78309700.0,104705800.0,507244300.0,0,0.0,2.3583515116010294,9.048999698589489
qqq_open,4173.0,264.66315761306276,149.26609884792612,82.94726881152158,135.00997000174164,228.16843046610649,360.5585501893892,635.4600219726562,0,0.0,0.689500852947855,-0.5600818004520698
qqq_high,4173.0,266.52342560317925,150.22910636864123,84.9287597208677,135.3305448184525,229.63131159699964,363.76171108454395,636.5999755859375,0,0.0,0.6828717504072421,-0.5724029786729403
qqq_low,4173.0,262.576106153702,148.12495285108804,78.3856745353014,133.97923449044086,225.36044118166936,358.8443784951762,631.8099975585938,0,0.0,0.6943364839715259,-0.5531727270040747
qqq_volume,4173.0,42886581.69182842,22197799.322656546,7079300.0,26443500.0,38263400.0,54254100.0,198685800.0,0,0.0,1.4522712617141442,3.3206233701678496
iwm_open,4173.0,159.21825341257755,43.51168107515046,82.64251408177331,123.1934163001263,151.9163787222345,196.80239636933533,269.8299865722656,0,0.0,0.273979764032966,-0.9469788086066252
iwm_high,4173.0,160.43644285782918,43.8765188371941,83.80203886115568,123.74951704574706,152.93493647041967,198.41210635278776,271.6000061035156,0,0.0,0.2721825506898502,-0.957170997840755
iwm_low,4173.0,157.85330225663583,43.10166553035626,82.25600358802109,122.48285451403368,151.07830421552646,195.00659705328547,269.4200134277344,0,0.0,0.2765864394725455,-0.9360873721055216
iwm_volume,4173.0,30139081.931464173,13294585.67710864,1200.0,21006500.0,27141300.0,35994400.0,123015100.0,0,0.0,1.5915684688988414,4.075600056402112
btc_usd_open,4173.0,27492.11101357382,32057.33292528637,176.89700317382812,2806.929931640625,10977.400390625,43012.234375,124752.140625,0,0.0,1.277872099156315,0.598652791983048
btc_usd_high,4173.0,28040.7123126522,32599.147048986848,211.7310028076172,2897.449951171875,11320.2001953125,43810.83203125,126198.0703125,0,0.0,1.2646133416779195,0.5525461487776302
btc_usd_low,4173.0,26904.60437247932,31467.187753619273,171.50999450683594,2690.840087890625,10667.28125,42189.30859375,123196.046875,0,0.0,1.292567608075603,0.6515682606451385
btc_usd_volume,4173.0,21920494900.1711,23025067114.51196,5914570.0,1380099968.0,17273093144.0,33723620826.0,350967941479.0,0,0.0,1.9832669084827756,12.22023938264432
fed_funds_rate,4173.0,1.9748933620896236,1.9111319374260352,0.04,0.13,1.42,4.09,5.33,0,0.0,0.6033187167890729,-1.1701933376464388
treasury_10y,4173.0,2.6558710759645336,1.1242786926614323,0.52,1.79,2.4,3.75,4.98,0,0.0,0.194501716427257,-1.0134535892126606
treasury_2y,4173.0,2.141071171818835,1.5861212928019908,0.09,0.7,1.68,3.68,5.19,0,0.0,0.3588651199641885,-1.3019998257143286
cpi,4173.0,271.7556975796789,30.245822735936887,234.747,244.243,259.127,302.845,326.588,0,0.0,0.4802498821451269,-1.31419577083434
unemployment,4173.0,4.668943206326384,1.6289017645832693,3.4,3.8,4.2,5.0,14.8,0,0.0,3.651921945648084,16.462650386751275
industrial_production,4173.0,100.35905044332613,2.6398295456277556,84.5619,99.5298,100.8639,101.4785,104.1004,0,0.0,-3.0109444508717966,14.37037227101418
yield_spread_10y_2y,4173.0,0.5147999041456984,0.6551229927633149,-1.0800000000000003,0.1599999999999997,0.52,1.02,2.04,0,0.0,-0.1416402427216452,-0.5870072173013687
ff_mkt_rf,4129.0,0.0005261564543472,0.011366015651854,-0.1201,-0.004,0.0008,0.006,0.0965,44,1.05,-0.2525143050642619,12.194677239714588
ff_smb,4129.0,-3.94768709130541e-06,0.0064588865539381,-0.0353,-0.0039,-0.0001,0.0037,0.0545,44,1.05,0.349955800551945,2.564414480122326
ff_hml,4129.0,1.4337612012593827e-05,0.0084547955982323,-0.0503,-0.0045,-0.0004,0.0040999999999999,0.0673,44,1.05,0.3059929074050738,4.231079041464999
ff_rf,4129.0,7.764591910874306e-05,8.497422992525306e-05,0.0,0.0,0.0001,0.0002,0.0002,44,1.05,0.4432132784913156,-1.4730361025744545
```

### `app/reports/metrics/target_variable_stats.csv`
- Shape: `4 rows x 9 cols`
```csv
Unnamed: 0,mean,std,skew,kurtosis,pct_positive,min,max,sharpe_approx
1d,0.0003416232108745,0.0092414214039365,-0.6444456275703175,22.40784969861708,0.3772770853307766,-0.1158865519715296,0.0998628977126859,0.5868253498383076
5d,0.0016993195920593,0.0196204555205108,-0.9076873493152544,8.729366833819247,0.5974088291746641,-0.1814076388264637,0.1324382000550112,0.6148670874494779
10d,0.003426306981922,0.0267561243574935,-1.360687668067866,8.582206449902,0.6279125630554888,-0.2257063408490894,0.13415943605127,0.6428406563163415
21d,0.0072742202070273,0.0383040227546533,-1.4906114138960735,8.930916426434486,0.6782273603082851,-0.3208215029783405,0.2122207091426108,0.6578587875595905
```

### `app/data/processed/missing_value_report.csv`
- Shape: `38 rows x 4 cols`
```csv
column,missing_before_cleaning,missing_after_cleaning,values_filled
spy,1301,0,1301
qqq,1301,0,1301
iwm,1301,0,1301
btc_usd,2443,0,2443
vix,1301,0,1301
xlf,1301,0,1301
xlk,1301,0,1301
xle,1301,0,1301
xlv,1301,0,1301
gld,1301,0,1301
uso,1620,0,1620
spy_open,1301,0,1301
spy_high,1301,0,1301
spy_low,1301,0,1301
spy_volume,1301,0,1301
qqq_open,1301,0,1301
qqq_high,1301,0,1301
qqq_low,1301,0,1301
qqq_volume,1301,0,1301
iwm_open,1301,0,1301
iwm_high,1301,0,1301
iwm_low,1301,0,1301
iwm_volume,1301,0,1301
btc_usd_open,2443,0,2443
btc_usd_high,2443,0,2443
btc_usd_low,2443,0,2443
btc_usd_volume,2443,0,2443
fed_funds_rate,0,0,0
treasury_10y,0,0,0
treasury_2y,0,0,0
cpi,0,0,0
unemployment,0,0,0
industrial_production,0,0,0
yield_spread_10y_2y,0,0,0
ff_mkt_rf,1333,44,1289
ff_smb,1333,44,1289
ff_hml,1333,44,1289
ff_rf,1333,44,1289
```

## Text Reports

### `app/reports/metrics/data_quality_report.txt`
```text
AEGIS V1 — Data Quality Report
==================================================

Universe: 4173 rows × 38 columns
Date range: 2014-09-17 → 2026-02-18
Total missing values: 176
Missing after forward-fill: 176

--- Feature Datasets ---
  qqq: 42 features × 3918 rows
    Missing: 0 (0.0000%)
```

## JSON Metrics (Full Contents)

### `app/data/processed/cleaning_log.json`
```json
[
  {
    "step": 0,
    "action": "Raw merge of all data sources",
    "rows_before": 6616,
    "rows_after": 6616,
    "cols": 38,
    "total_missing": 46488,
    "missing_pct": 18.4911,
    "detail": "Merged 11 OHLCV sources + FRED + Fama-French"
  },
  {
    "step": 1,
    "action": "Remove duplicate timestamps",
    "rows_before": 6616,
    "rows_after": 6616,
    "removed": 0,
    "detail": "Kept last value for 0 duplicate dates"
  },
  {
    "step": 2,
    "action": "Calendar alignment analysis",
    "rows_before": 6616,
    "rows_after": 6616,
    "detail": "BTC-only dates (weekends): 1301, SPY-only dates: 2443. Kept all dates; NaN indicates market closed."
  },
  {
    "step": 3,
    "action": "Forward-fill (limit=5 days, causal only \u2014 no backfill)",
    "missing_before": 46488,
    "missing_after": 12710,
    "values_filled": 33778,
    "detail": "Forward-fill propagates the last known value forward. Limit of 5 prevents filling across long data gaps (e.g., BTC not available before 2014). No backward fill is ever used \u2014 that would leak future data."
  },
  {
    "step": 4,
    "action": "Drop rows where any target instrument has NaN",
    "rows_before": 6616,
    "rows_after": 4173,
    "rows_dropped": 2443,
    "detail": "Dropped 2443 rows where at least one of ['spy', 'qqq', 'iwm', 'btc_usd'] was NaN. This aligns the dataset to the period where all instruments have data."
  },
  {
    "step": 5,
    "action": "Outlier detection (flagged, NOT removed)",
    "method": "Z-score > 4 on daily log returns",
    "outliers_per_instrument": {
      "spy": 31,
      "qqq": 26,
      "iwm": 20,
      "btc_usd": 26
    },
    "detail": "Extreme return outliers are FLAGGED but kept in the dataset. Removing them would erase real market events (crashes, squeezes). The regime model is expected to learn these as distinct market states."
  },
  {
    "step": 6,
    "action": "Final dataset state",
    "rows": 4173,
    "cols": 38,
    "total_missing": 176,
    "missing_pct": 0.111,
    "date_range": "2014-09-17 \u2192 2026-02-18",
    "detail": "Cleaned dataset ready for feature engineering."
  }
]
```

### `app/models/selection_metadata.json`
```json
{
  "regime_model": "GMM",
  "regime_k": 2,
  "regime_features": [
    "volatility_21d",
    "volatility_63d",
    "log_ret_21d",
    "rsi_14",
    "dist_sma_50",
    "dist_sma_200",
    "atr_norm",
    "volume_ratio_20d",
    "vix"
  ],
  "regime_silhouette": 0.3400461901985678,
  "regime_db": 1.4875406821377253,
  "signal_model": "LightGBM",
  "signal_features": [
    "log_ret_1d",
    "log_ret_5d",
    "volatility_10d",
    "volatility_21d",
    "dist_sma_10",
    "dist_sma_21",
    "dist_sma_50",
    "dist_sma_200",
    "ma_cross_10_50",
    "rsi_14",
    "roc_10",
    "atr_14",
    "atr_norm",
    "bollinger_pos",
    "volume_ratio_20d",
    "volume_change",
    "vix",
    "vix_change_1d",
    "yield_spread_10y_2y",
    "unemployment",
    "ff_mkt_rf",
    "ff_smb",
    "ff_hml",
    "ff_rf",
    "regime_label",
    "regime_prob_0",
    "regime_prob_1"
  ],
  "signal_auc": 0.5130359076409302,
  "signal_horizon": 5,
  "signal_threshold": 0.005,
  "n_folds": 5,
  "regime_names": {
    "0": "Crisis/High-Vol",
    "1": "Neutral"
  },
  "features_removed": [
    "volatility_63d",
    "xlf_spy_ratio",
    "mean_ret_63d",
    "industrial_production",
    "gold_equity_ratio",
    "volatility_5d",
    "mean_ret_21d",
    "log_ret_10d",
    "log_ret_21d",
    "volume_ma_20",
    "xlk_spy_ratio",
    "parkinson_vol_21d",
    "roc_21",
    "cpi",
    "treasury_10y",
    "fed_funds_rate",
    "treasury_2y"
  ]
}
```

## Metric Calculations Found In Code

### `app/pipelines/build_dataset.py`
- Keyword hits: `43`
```text
14: - backend/app/data/processed/universe.parquet      (unified daily dataset)
34: PROCESSED_DIR = BASE_DIR / "data" / "processed"
36: PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
50: "CPIAUCSL": "cpi",
198: 1. Merge raw sources → record initial missing values
204: 7. Detect price outliers (>10 std moves) and flag (don't remove)
234: raw_missing = universe.isnull().sum().to_dict()
235: raw_total_missing = universe.isnull().sum().sum()
236: raw_missing_pct = (raw_total_missing / universe.size * 100)
238: raw_snapshot_path = PROCESSED_DIR / "universe_raw_snapshot.parquet"
247: "total_missing": int(raw_total_missing),
248: "missing_pct": round(raw_missing_pct, 4),
251: print(f"\n  Step 0 — Raw merge: {raw_shape}, {raw_total_missing} missing values ({raw_missing_pct:.2f}%)")
289: missing_before_ffill = universe.isnull().sum().sum()
293: missing_after_ffill = universe.isnull().sum().sum()
294: filled_count = missing_before_ffill - missing_after_ffill
299: "missing_before": int(missing_before_ffill),
300: "missing_after": int(missing_after_ffill),
308: print(f"  Step 3 — Forward-fill: {filled_count} values filled ({missing_before_ffill} → {missing_after_ffill} missing)")
333: outlier_flags = pd.DataFrame(index=universe.index)
334: outlier_counts = {}
342: is_outlier = z_scores > 4
343: outlier_flags[f"{col}_outlier"] = is_outlier.astype(int)
344: outlier_counts[col] = int(is_outlier.sum())
346: outlier_flags.to_parquet(PROCESSED_DIR / "outlier_flags.parquet", engine="pyarrow")
350: "action": "Outlier detection (flagged, NOT removed)",
352: "outliers_per_instrument": outlier_counts,
354: "Extreme return outliers are FLAGGED but kept in the dataset. "
359: print(f"  Step 5 — Outliers flagged (z>4): {outlier_counts}")
361: final_missing = universe.isnull().sum().sum()
362: final_missing_pct = final_missing / universe.size * 100
369: "total_missing": int(final_missing),
370: "missing_pct": round(final_missing_pct, 4),
375: path = PROCESSED_DIR / "universe.parquet"
379: log_path = PROCESSED_DIR / "cleaning_log.json"
383: missing_report = pd.DataFrame({
385: "missing_before_cleaning": [raw_missing.get(c, 0) for c in universe.columns],
386: "missing_after_cleaning": [universe[c].isnull().sum() for c in universe.columns],
388: missing_report["values_filled"] = missing_report["missing_before_cleaning"] - missing_report["missing_after_cleaning"]
389: missing_report.to_csv(PROCESSED_DIR / "missing_value_report.csv", index=False)
394: print(f"  Raw:     {raw_shape[0]} rows × {raw_shape[1]} cols, {raw_total_missing} missing ({raw_missing_pct:.2f}%)")
395: print(f"  Cleaned: {len(universe)} rows × {len(universe.columns)} cols, {final_missing} missing ({final_missing_pct:.2f}%)")
419: print(f"  Processed file: {PROCESSED_DIR / 'universe.parquet'}")
```

### `app/pipelines/eda.py`
- Keyword hits: `143`
```text
8: 2.  missing_values_heatmap.png      — Missing data pattern visualization
9: 3.  missing_values_summary.csv      — Missing counts per column
14: 8.  pca_variance_explained.png      — PCA cumulative variance
15: 9.  pca_2d_scatter.png              — First 2 principal components
16: 10. outlier_boxplots.png            — Box plots for return features
17: 11. outlier_zscore_timeseries.png   — Z-score flagged outliers over time
38: from sklearn.decomposition import PCA
39: from sklearn.preprocessing import StandardScaler
47: PROCESSED_DIR = BASE_DIR / "data" / "processed"
64: universe = pd.read_parquet(PROCESSED_DIR / "universe.parquet")
87: desc["missing"] = universe.isnull().sum()
88: desc["missing_pct"] = (universe.isnull().sum() / len(universe) * 100).round(2)
89: desc["skewness"] = universe.skew()
90: desc["kurtosis"] = universe.kurtosis()
92: print(f"       Saved summary_statistics.csv ({len(desc)} variables)")
96: def plot_missing_values(universe: pd.DataFrame):
97: """Visualize missing data patterns."""
98: print("  [2/16] Missing value analysis...")
100: missing = universe.isnull().sum()
101: missing_pct = (missing / len(universe) * 100).round(2)
102: missing_df = pd.DataFrame({"count": missing, "percent": missing_pct})
103: missing_df = missing_df[missing_df["count"] > 0].sort_values("percent", ascending=False)
104: missing_df.to_csv(METRICS_DIR / "missing_values_summary.csv")
108: if len(missing_df) > 0:
109: cols_to_show = missing_df.head(20)
113: axes[0].set_xlabel("Missing (%)")
114: axes[0].set_title("Missing Values by Column (Top 20)")
117: axes[0].text(0.5, 0.5, "No missing values!", ha="center", va="center", fontsize=14)
118: axes[0].set_title("Missing Values by Column")
122: axes[1].set_title("Missing Data Pattern (sampled)")
127: plt.savefig(FIGURES_DIR / "missing_values_heatmap.png", dpi=DPI, bbox_inches="tight")
129: print(f"       {len(missing_df)} columns with missing data")
195: ax.legend([f"KDE (skew={returns.skew():.2f}, kurt={returns.kurtosis():.2f})", "Normal"])
220: variances = numeric.var().sort_values(ascending=False)
221: top_cols = variances.head(30).index.tolist()
236: ax.set_title("Feature Correlation Matrix (SPY — Top 30 by Variance)", fontsize=13)
269: def plot_pca_analysis(features: dict):
270: """PCA variance explained and 2D projection."""
271: print("  [7/16] PCA analysis...")
285: pca = PCA(n_components=n_components)
286: X_pca = pca.fit_transform(X_scaled)
288: cum_var = np.cumsum(pca.explained_variance_ratio_) * 100
292: axes[0].bar(range(1, n_components + 1), pca.explained_variance_ratio_ * 100,
299: axes[0].set_ylabel("Variance Explained (%)")
300: axes[0].set_title("PCA — Variance Explained")
303: scatter = axes[1].scatter(X_pca[:, 0], X_pca[:, 1], c=range(len(X_pca)),
305: axes[1].set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
306: axes[1].set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
307: axes[1].set_title("PCA — 2D Projection (color = time)")
311: plt.savefig(FIGURES_DIR / "pca_variance_explained.png", dpi=DPI, bbox_inches="tight")
314: pca_stats = pd.DataFrame({
316: "variance_explained": pca.explained_variance_ratio_,
317: "cumulative_variance": cum_var / 100,
319: pca_stats.to_csv(METRICS_DIR / "pca_stats.csv", index=False)
320: print(f"       {n_90} components needed for 90% variance")
323: def plot_outlier_analysis(features: dict):
324: """Box plots and z-score outlier detection."""
325: print("  [8/16] Outlier analysis...")
333: return_cols = [c for c in df.columns if "ret" in c or "roc" in c][:8]
347: outlier_mask = z_scores > 3
351: axes[1].scatter(dates[outlier_mask], returns.dropna().values[outlier_mask],
352: color="#e74c3c", s=20, zorder=5, label=f"Outliers (|z| > 3): {outlier_mask.sum()}")
353: axes[1].set_title("Daily Log Returns with Z-Score Outliers (SPY)")
359: plt.savefig(FIGURES_DIR / "outlier_analysis.png", dpi=DPI, bbox_inches="tight")
365: outlier_summary = pd.DataFrame({
367: "n_outliers": [(z > t).sum() for t in [2, 2.5, 3, 3.5]],
368: "pct_outliers": [((z > t).sum() / len(z) * 100).round(2) for t in [2, 2.5, 3, 3.5]],
370: outlier_summary.to_csv(METRICS_DIR / "outlier_summary.csv", index=False)
371: print(f"       {(z > 3).sum()} outliers at z > 3 threshold")
376: print("  [9/16] Rolling volatility comparison...")
498: "rsi_14", "roc_10",
529: def plot_rsi_comparison(features: dict):
530: """RSI distribution comparison across instruments."""
531: print("  [13/16] RSI comparison...")
587: def plot_sector_comparison(universe: pd.DataFrame):
589: print("  [15/16] Sector ETF comparison...")
614: plt.savefig(FIGURES_DIR / "sector_comparison.png", dpi=DPI, bbox_inches="tight")
627: lines.append(f"Total missing values: {universe.isnull().sum().sum()}")
628: lines.append(f"Missing after forward-fill: {universe.isnull().sum().sum()}")
634: missing = df.isnull().sum().sum()
635: lines.append(f"    Missing: {missing} ({missing / df.size * 100:.4f}%)")
647: Visualize the data cleaning process: before vs after.
652: raw_path = PROCESSED_DIR / "universe_raw_snapshot.parquet"
653: log_path = PROCESSED_DIR / "cleaning_log.json"
654: missing_report_path = PROCESSED_DIR / "missing_value_report.csv"
665: raw_missing = raw.isnull().sum().sort_values(ascending=False)
666: raw_missing_pct = (raw_missing / len(raw) * 100)
667: top_missing = raw_missing_pct[raw_missing_pct > 0].head(15)
669: if len(top_missing) > 0:
670: axes[0, 0].barh(range(len(top_missing)), top_missing.values, color="#e74c3c", alpha=0.8)
671: axes[0, 0].set_yticks(range(len(top_missing)))
672: axes[0, 0].set_yticklabels(top_missing.index, fontsize=9)
673: axes[0, 0].set_xlabel("Missing (%)")
674: axes[0, 0].set_title("BEFORE Cleaning — Missing Values (Top 15)", fontweight="bold")
677: axes[0, 0].text(0.5, 0.5, "No missing values in raw data", ha="center", va="center")
680: clean_missing = universe.isnull().sum().sort_values(ascending=False)
681: clean_missing_pct = (clean_missing / len(universe) * 100)
682: top_clean = clean_missing_pct[clean_missing_pct > 0].head(15)
688: axes[0, 1].set_xlabel("Missing (%)")
689: axes[0, 1].set_title("AFTER Cleaning — Missing Values (Top 15)", fontweight="bold")
692: axes[0, 1].text(0.5, 0.5, "All missing values resolved!", ha="center", va="center", fontsize=13, color="#2ecc71")
717: if missing_report_path.exists():
718: mr = pd.read_csv(missing_report_path)
719: mr = mr[mr["missing_before_cleaning"] > 0].sort_values("missing_before_cleaning", ascending=False).head(12)
723: axes[1, 1].bar([i - width/2 for i in x], mr["missing_before_cleaning"], width,
725: axes[1, 1].bar([i + width/2 for i in x], mr["missing_after_cleaning"], width,
729: axes[1, 1].set_ylabel("Missing Count")
730: axes[1, 1].set_title("Per-Column Missing: Before vs After", fontweight="bold")
733: axes[1, 1].text(0.5, 0.5, "Missing report not found", ha="center", va="center")
735: plt.suptitle("Data Cleaning Process — Before vs After", fontsize=15, fontweight="bold", y=1.02)
801: def plot_target_variable_exploration(universe: pd.DataFrame):
803: Explore the target variable: forward returns.
807: print("  [19/20] Target variable exploration...")
869: rolling_sharpe = rolling_mean / rolling_std
870: ax.plot(rolling_sharpe.index, rolling_sharpe.values, linewidth=0.8, color="#9b59b6")
872: ax.axhline(1, color="green", linestyle=":", alpha=0.5, label="Sharpe = 1")
873: ax.axhline(-1, color="red", linestyle=":", alpha=0.5, label="Sharpe = -1")
875: ax.set_ylabel("Rolling Sharpe (63d)")
876: ax.set_title("Rolling Sharpe Ratio — Market Regime Proxy")
880: plt.suptitle("Target Variable Analysis: Forward Returns", fontsize=14, fontweight="bold", y=1.02)
882: plt.savefig(FIGURES_DIR / "target_variable_exploration.png", dpi=DPI, bbox_inches="tight")
891: "skew": r.skew(),
892: "kurtosis": r.kurtosis(),
896: "sharpe_approx": r.mean() / r.std() * np.sqrt(252 / int(label.replace("d", ""))),
898: pd.DataFrame(target_stats).T.to_csv(METRICS_DIR / "target_variable_stats.csv")
899: print("       Saved target_variable_stats.csv")
902: def plot_stationarity_check(universe: pd.DataFrame):
904: Visual stationarity check: raw price (non-stationary) vs returns (stationary).
905: Includes rolling mean and variance to show the difference.
907: print("  [20/20] Stationarity check...")
927: axes[0, 1].set_title("SPY Price — Rolling Variance (non-constant)", fontweight="bold")
928: axes[0, 1].set_ylabel("Variance")
940: axes[1, 1].set_title("SPY Returns — Rolling Variance (more stable)", fontweight="bold")
941: axes[1, 1].set_ylabel("Variance")
946: plt.suptitle("Stationarity: Why We Transform Prices → Returns", fontsize=14, fontweight="bold", y=1.02)
948: plt.savefig(FIGURES_DIR / "stationarity_check.png", dpi=DPI, bbox_inches="tight")
961: plot_missing_values(universe)
966: plot_pca_analysis(features)
967: plot_outlier_analysis(features)
972: plot_rsi_comparison(features)
974: plot_sector_comparison(universe)
978: plot_target_variable_exploration(universe)
979: plot_stationarity_check(universe)
```

### `app/pipelines/feature_engineering.py`
- Keyword hits: `10`
```text
36: PROCESSED_DIR = BASE_DIR / "data" / "processed"
80: loss = -delta.where(delta < 0, 0.0)
83: avg_loss = loss.rolling(window=period, min_periods=period).mean()
85: rs = avg_gain / avg_loss.replace(0, np.nan)
94: tr2 = (high - prev_close).abs()
96: true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
177: features["roc_10"] = compute_rate_of_change(close, period=10)
178: features["roc_21"] = compute_rate_of_change(close, period=21)
179: print(f"    ROC: roc_10, roc_21")
253: universe_path = PROCESSED_DIR / "universe.parquet"
```

### `app/data/AEGIS_Model_Exploration.ipynb`
- Keyword hits: `207`
```text
54: "from sklearn.preprocessing import StandardScaler\n",
56: "    silhouette_score, davies_bouldin_score, calinski_harabasz_score,\n",
57: "    accuracy_score, precision_score, recall_score, f1_score,\n",
58: "    roc_auc_score, classification_report, confusion_matrix,\n",
59: "    RocCurveDisplay\n",
99: "PROCESSED_DIR = BASE / 'processed'\n",
108: "universe = pd.read_parquet(PROCESSED_DIR / 'universe.parquet')\n",
174: "We test GMM with 2-6 components and use BIC/AIC and Silhouette Score to determine the optimal number of regimes."
186: "  k=2: BIC=50988, Silhouette=0.3400, Davies-Bouldin=1.4875\n",
187: "  k=3: BIC=47093, Silhouette=0.2083, Davies-Bouldin=1.7881\n",
188: "  k=4: BIC=46409, Silhouette=0.2020, Davies-Bouldin=1.7331\n",
189: "  k=5: BIC=45752, Silhouette=0.1407, Davies-Bouldin=1.6222\n",
190: "  k=6: BIC=44788, Silhouette=0.1369, Davies-Bouldin=1.6611\n"
195: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjYAAAGGCAYAAADYTbhfAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3Qd4U9UbBvC3G2gZBUrZsje...
208: "Optimal k by Silhouette: 2\n",
219: "    gmm = GaussianMixture(n_components=k, covariance_type='full', n_init=5, random_state=42)\n",
221: "    sil = silhouette_score(X_regime, labels)\n",
222: "    db = davies_bouldin_score(X_regime, labels)\n",
223: "    ch = calinski_harabasz_score(X_regime, labels)\n",
225: "                      'silhouette': sil, 'davies_bouldin': db, 'calinski_harabasz': ch})\n",
226: "    print(f'  k={k}: BIC={gmm.bic(X_regime):.0f}, Silhouette={sil:.4f}, Davies-Bouldin={db:.4f}')\n",
239: "axes[1].plot(list(k_range), results_k_df['silhouette'], 'g-o')\n",
241: "axes[1].set_ylabel('Silhouette Score')\n",
242: "axes[1].set_title('Silhouette Score (higher = better)')\n",
244: "axes[2].plot(list(k_range), results_k_df['davies_bouldin'], 'm-o')\n",
246: "axes[2].set_ylabel('Davies-Bouldin Index')\n",
247: "axes[2].set_title('Davies-Bouldin Index (lower = better)')\n",
254: "best_k = results_k_df.loc[results_k_df['silhouette'].idxmax(), 'k']\n",
255: "print(f'\\nOptimal k by Silhouette: {best_k}')\n",
278: "  Silhouette Score:      0.3400\n",
279: "  Davies-Bouldin Index:  1.4875\n",
280: "  Calinski-Harabasz:     1343.02\n",
288: "gmm = GaussianMixture(n_components=REGIME_K, covariance_type='full', n_init=10, random_state=42)\n",
293: "gmm_silhouette = silhouette_score(X_regime, gmm_labels)\n",
294: "gmm_db = davies_bouldin_score(X_regime, gmm_labels)\n",
295: "gmm_ch = calinski_harabasz_score(X_regime, gmm_labels)\n",
298: "print(f'  Silhouette Score:      {gmm_silhouette:.4f}')\n",
299: "print(f'  Davies-Bouldin Index:  {gmm_db:.4f}')\n",
300: "print(f'  Calinski-Harabasz:     {gmm_ch:.2f}')\n",
382: "GMM Label Stability (Adjusted Rand Index across 5 seeds):\n",
383: "  Mean ARI: 1.0000 (1.0 = perfect agreement)\n",
384: "  Min ARI:  1.0000\n",
385: "  Max ARI:  1.0000\n"
390: "# ─── GMM STABILITY TEST ──────────────────────────────────────\n",
395: "    g = GaussianMixture(n_components=REGIME_K, covariance_type='full', n_init=10, random_state=s)\n",
400: "ari_scores = []\n",
403: "        ari = adjusted_rand_score(all_labels[i], all_labels[j])\n",
404: "        ari_scores.append(ari)\n",
406: "gmm_stability = np.mean(ari_scores)\n",
407: "print(f'GMM Label Stability (Adjusted Rand Index across {len(seeds)} seeds):')\n",
408: "print(f'  Mean ARI: {gmm_stability:.4f} (1.0 = perfect agreement)')\n",
409: "print(f'  Min ARI:  {np.min(ari_scores):.4f}')\n",
410: "print(f'  Max ARI:  {np.max(ari_scores):.4f}')"
430: "  Silhouette Score:      0.2507\n",
431: "  Davies-Bouldin Index:  1.6978\n",
432: "  Calinski-Harabasz:     1009.22\n",
447: "    covariance_type='full',\n",
457: "hmm_silhouette = silhouette_score(X_regime, hmm_labels)\n",
458: "hmm_db = davies_bouldin_score(X_regime, hmm_labels)\n",
459: "hmm_ch = calinski_harabasz_score(X_regime, hmm_labels)\n",
462: "print(f'  Silhouette Score:      {hmm_silhouette:.4f}')\n",
463: "print(f'  Davies-Bouldin Index:  {hmm_db:.4f}')\n",
464: "print(f'  Calinski-Harabasz:     {hmm_ch:.2f}')\n",
521: "HMM Label Stability (ARI across 5 seeds):\n",
522: "  Mean ARI: 0.9107\n",
523: "  Min ARI:  0.7767\n",
524: "  Max ARI:  1.0000\n"
529: "# ─── HMM STABILITY TEST ──────────────────────────────────────\n",
530: "ari_hmm = []\n",
533: "        h1 = GaussianHMM(n_components=REGIME_K, covariance_type='full', n_iter=200, random_state=seeds[i])\n",
534: "        h2 = GaussianHMM(n_components=REGIME_K, covariance_type='full', n_iter=200, random_state=seeds[j])\n",
537: "        ari = adjusted_rand_score(h1.predict(X_regime), h2.predict(X_regime))\n",
538: "        ari_hmm.append(ari)\n",
540: "hmm_stability = np.mean(ari_hmm)\n",
541: "print(f'HMM Label Stability (ARI across {len(seeds)} seeds):')\n",
542: "print(f'  Mean ARI: {hmm_stability:.4f}')\n",
543: "print(f'  Min ARI:  {np.min(ari_hmm):.4f}')\n",
544: "print(f'  Max ARI:  {np.max(ari_hmm):.4f}')"
551: "## 1.4 Regime Model Comparison"
563: "Regime Model Comparison:\n",
565: "     Silhouette Score                        0.3400                  0.2507    GMM\n",
566: " Davies-Bouldin Index                        1.4875                  1.6978    GMM\n",
567: "    Calinski-Harabasz                       1343.02                 1009.22    GMM\n",
568: "Label Stability (ARI)                        1.0000                  0.9107    GMM\n",
574: "# ─── COMPARISON TABLE ────────────────────────────────────────\n",
575: "comparison_regime = pd.DataFrame({\n",
576: "    'Metric': ['Silhouette Score', 'Davies-Bouldin Index', 'Calinski-Harabasz',\n",
577: "               'Label Stability (ARI)', 'Regime Persistence'],\n",
579: "        f'{gmm_silhouette:.4f}',\n",
582: "        f'{gmm_stability:.4f}',\n",
586: "        f'{hmm_silhouette:.4f}',\n",
589: "        f'{hmm_stability:.4f}',\n",
593: "        'GMM' if gmm_silhouette > hmm_silhouette else 'HMM',\n",
596: "        'GMM' if gmm_stability > hmm_stability else 'HMM',\n",
600: "print('Regime Model Comparison:')\n",
601: "print(comparison_regime.to_string(index=False))\n",
602: "comparison_regime.to_csv(METRICS_DIR / 'regime_model_comparison.csv', index=False)"
612: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjYAAASlCAYAAAALTeBgAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3Qd8VHW6PvBnesukQwghhE6...
667: "axes[2].set_title(f'Regime Stability: GMM={gmm_transitions} transitions, HMM={hmm_transitions} transitions')\n",
673: "plt.savefig(FIGURES_DIR / 'regime_comparison_timeline.png', dpi=DPI, bbox_inches='tight')\n",
732: "image/png": "iVBORw0KGgoAAAANSUhEUgAABTwAAAHpCAYAAACvL/MYAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAgkpJREFUeJzt3Qd4FNX38PGzARJCh4TepSg...
786: "Based on the comparison above, we select the final regime model."
811: "# Score: higher silhouette + lower DB + fewer transitions (more stable) + better event alignment\n",
812: "gmm_score = (gmm_silhouette * 2) - (gmm_db * 0.5) + (gmm_stability * 1)\n",
813: "hmm_score = (hmm_silhouette * 2) - (hmm_db * 0.5) + (hmm_stability * 1)\n",
844: "regime_output.to_parquet(PROCESSED_DIR / 'regime_assignments.parquet')\n",
857: "2. **XGBoost** — gradient-boosted trees (regularized, robust)\n",
938: "# Create fold boundaries\n",
965: "  Fold 1: Acc=0.4760, F1=0.6039, AUC=0.4727\n",
966: "  Fold 2: Acc=0.5048, F1=0.5845, AUC=0.5008\n",
967: "  Fold 3: Acc=0.4505, F1=0.5222, AUC=0.4451\n",
968: "  Fold 4: Acc=0.6677, F1=0.7426, AUC=0.6099\n",
969: "  Fold 5: Acc=0.5335, F1=0.6313, AUC=0.5152\n",
972: "  Fold 1: Acc=0.5335, F1=0.5989, AUC=0.4889\n",
973: "  Fold 2: Acc=0.4505, F1=0.5657, AUC=0.4848\n",
974: "  Fold 3: Acc=0.4313, F1=0.4855, AUC=0.4547\n",
975: "  Fold 4: Acc=0.6102, F1=0.7067, AUC=0.5491\n",
976: "  Fold 5: Acc=0.5687, F1=0.6494, AUC=0.5547\n",
979: "  Fold 1: Acc=0.5048, F1=0.6056, AUC=0.5557\n",
980: "  Fold 2: Acc=0.5016, F1=0.5667, AUC=0.5022\n",
981: "  Fold 3: Acc=0.6262, F1=0.7394, AUC=0.4944\n",
982: "  Fold 4: Acc=0.6358, F1=0.7683, AUC=0.5493\n",
983: "  Fold 5: Acc=0.6645, F1=0.7904, AUC=0.5360\n",
986: "  Fold 1: Acc=0.4856, F1=0.6538, AUC=0.4778\n",
987: "  Fold 2: Acc=0.6677, F1=0.7547, AUC=0.7179\n",
988: "  Fold 3: Acc=0.6677, F1=0.7984, AUC=0.6596\n",
989: "  Fold 4: Acc=0.6326, F1=0.7677, AUC=0.5120\n",
990: "  Fold 5: Acc=0.6326, F1=0.7750, AUC=0.6212\n",
1010: "        random_state=42, use_label_encoder=False, eval_metric='logloss', verbosity=0\n",
1042: "        acc = accuracy_score(y_test, y_pred)\n",
1043: "        prec = precision_score(y_test, y_pred, zero_division=0)\n",
1044: "        rec = recall_score(y_test, y_pred, zero_division=0)\n",
1045: "        f1 = f1_score(y_test, y_pred, zero_division=0)\n",
1047: "            auc = roc_auc_score(y_test, y_proba)\n",
1049: "            auc = 0.5\n",
1052: "            'fold': fold_idx + 1, 'accuracy': acc, 'precision': prec,\n",
1053: "            'recall': rec, 'f1': f1, 'auc_roc': auc\n",
1057: "        print(f'  Fold {fold_idx+1}: Acc={acc:.4f}, F1={f1:.4f}, AUC={auc:.4f}')\n",
1066: "## 2.1 Signal Model Comparison"
1078: "Signal Model Comparison (Walk-Forward CV):\n",
1079: "              Model Accuracy (mean) Accuracy (std) Precision (mean) Recall (mean) F1 (mean) AUC-ROC (mean)\n",
1094: "        'Accuracy (mean)': f\"{rdf['accuracy'].mean():.4f}\",\n",
1095: "        'Accuracy (std)': f\"{rdf['accuracy'].std():.4f}\",\n",
1096: "        'Precision (mean)': f\"{rdf['precision'].mean():.4f}\",\n",
1097: "        'Recall (mean)': f\"{rdf['recall'].mean():.4f}\",\n",
1098: "        'F1 (mean)': f\"{rdf['f1'].mean():.4f}\",\n",
1099: "        'AUC-ROC (mean)': f\"{rdf['auc_roc'].mean():.4f}\",\n",
1103: "print('Signal Model Comparison (Walk-Forward CV):')\n",
1105: "summary_df.to_csv(METRICS_DIR / 'signal_model_comparison.csv', index=False)"
1115: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjYAAAHqCAYAAACne3d+AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzsnQeYFFXWhr+Ok3Me0jDknBE...
1125: "# ─── VISUALIZATION: MODEL COMPARISON ─────────────────────────\n",
1131: "# Accuracy across folds\n",
1134: "    axes[0].plot(rdf['fold'], rdf['accuracy'], '-o', label=name, color=colors_models[idx])\n",
1136: "axes[0].set_ylabel('Accuracy')\n",
1137: "axes[0].set_title('Accuracy Across Walk-Forward Folds')\n",
1141: "# F1 across folds\n",
1144: "    axes[1].plot(rdf['fold'], rdf['f1'], '-o', label=name, color=colors_models[idx])\n",
1146: "axes[1].set_ylabel('F1 Score')\n",
1147: "axes[1].set_title('F1 Score Across Walk-Forward Folds')\n",
1151: "metrics_to_plot = ['accuracy', 'f1', 'auc_roc']\n",
1159: "axes[2].set_xticklabels(['Accuracy', 'F1', 'AUC-ROC'])\n",
1161: "axes[2].set_title('Mean Metrics Comparison')\n",
1166: "plt.savefig(FIGURES_DIR / 'signal_model_comparison.png', dpi=DPI, bbox_inches='tight')\n",
1177: "image/png": "iVBORw0KGgoAAAANSUhEUgAABuwAAAGdCAYAAAD5b1WHAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAxRJJREFUeJzs3Qd4VNXWxvGV0DtSpUmv0kF...
1214: "image/png": "iVBORw0KGgoAAAANSUhEUgAAAwkAAAMWCAYAAAC6G8rCAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3Qd4VFX6BvB3WnqvBEIJhN6...
1224: "# ─── ROC CURVES ──────────────────────────────────────────────\n",
1232: "        auc = roc_auc_score(y_true, y_proba)\n",
1233: "        RocCurveDisplay.from_predictions(y_true, y_proba, name=f'{name} (AUC={auc:.3f})',\n",
1238: "ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Random (AUC=0.5)')\n",
1239: "ax.set_title('ROC Curves — All Signal Model Candidates')\n",
1242: "plt.savefig(FIGURES_DIR / 'signal_roc_curves.png', dpi=DPI, bbox_inches='tight')\n",
1260: "image/png": "iVBORw0KGgoAAAANSUhEUgAAA90AAAMWCAYAAADs4eXxAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAq7JJREFUeJzs3QmYjfX///E3Y2eQomwhJJW...
1327: "Evaluate if signal model performance varies by detected regime."
1340: "Regime                    N   Accuracy       F1\n",
1360: "print(f'{\"Regime\":20s} {\"N\":>6s} {\"Accuracy\":>10s} {\"F1\":>8s}')\n",
1369: "    acc = accuracy_score(y_test_final[mask], y_pred_final[mask])\n",
1370: "    f1 = f1_score(y_test_final[mask], y_pred_final[mask], zero_division=0)\n",
1371: "    regime_perf.append({'Regime': r_name, 'N': int(mask.sum()), 'Accuracy': acc, 'F1': f1})\n",
1372: "    print(f'{r_name:20s} {mask.sum():>6d} {acc:>10.4f} {f1:>8.4f}')\n",
1401: "  Silhouette: 0.3400\n",
1402: "  Davies-Bouldin: 1.4875\n",
1403: "  Stability (ARI): 1.0000\n",
1408: "  Mean AUC-ROC: 0.5977\n",
1409: "  Mean Accuracy: 0.6173\n",
1410: "  Mean F1: 0.7499\n",
1417: "# Find best signal model by mean AUC-ROC\n",
1418: "best_signal = max(all_results.items(), key=lambda x: pd.DataFrame(x[1])['auc_roc'].mean())\n",
1420: "best_signal_auc = pd.DataFrame(best_signal[1])['auc_roc'].mean()\n",
1427: "print(f'  Silhouette: {hmm_silhouette if selected_regime==\"HMM\" else gmm_silhouette:.4f}')\n",
1428: "print(f'  Davies-Bouldin: {hmm_db if selected_regime==\"HMM\" else gmm_db:.4f}')\n",
1429: "print(f'  Stability (ARI): {hmm_stability if selected_regime==\"HMM\" else gmm_stability:.4f}')\n",
1433: "print(f'  Mean AUC-ROC: {best_signal_auc:.4f}')\n",
1435: "print(f'  Mean Accuracy: {best_df[\"accuracy\"].mean():.4f}')\n",
1436: "print(f'  Mean F1: {best_df[\"f1\"].mean():.4f}')\n",
1471: "    'regime_silhouette': float(hmm_silhouette if selected_regime == 'HMM' else gmm_silhouette),\n",
1472: "    'regime_davies_bouldin': float(hmm_db if selected_regime == 'HMM' else gmm_db),\n",
1475: "    'signal_auc': float(best_signal_auc),\n",
1496: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjUAAATNCAYAAAAE3dZUAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3QWYXNX5x/F3ZC27m427hwg...
1520: "# Top-right: Signal model comparison bars\n",
1522: "aucs = [pd.DataFrame(all_results[n])['auc_roc'].mean() for n in model_names]\n",
1524: "axes[0, 1].bar(model_names_short, aucs, color=bar_colors)\n",
1525: "axes[0, 1].set_ylabel('Mean AUC-ROC')\n",
1529: "for i, v in enumerate(aucs):\n",
1544: "    r_accs = [r['Accuracy'] for r in regime_perf]\n",
1545: "    r_f1s = [r['F1'] for r in regime_perf]\n",
1547: "    axes[1, 1].bar(x - 0.15, r_accs, 0.3, label='Accuracy', color='#3498db')\n",
1548: "    axes[1, 1].bar(x + 0.15, r_f1s, 0.3, label='F1', color='#e74c3c')\n",
```

### `app/data/AEGIS_Model_Exploration_V2.ipynb`
- Keyword hits: `235`
```text
29: "from sklearn.preprocessing import StandardScaler\n",
31: "    silhouette_score, davies_bouldin_score, calinski_harabasz_score,\n",
32: "    accuracy_score, precision_score, recall_score, f1_score,\n",
33: "    roc_auc_score, classification_report, confusion_matrix,\n",
34: "    RocCurveDisplay, adjusted_rand_score\n",
74: "PROCESSED_DIR = BASE / 'processed'\n",
82: "universe = pd.read_parquet(PROCESSED_DIR / 'universe.parquet')\n",
150: "  k=2: BIC=50988, Silhouette=0.3400, DB=1.4875\n",
151: "  k=3: BIC=47093, Silhouette=0.2083, DB=1.7881\n",
152: "  k=4: BIC=46409, Silhouette=0.2020, DB=1.7331\n",
153: "  k=5: BIC=45752, Silhouette=0.1407, DB=1.6222\n",
154: "  k=6: BIC=44788, Silhouette=0.1369, DB=1.6611\n"
159: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjYAAAGGCAYAAADYTbhfAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3QmcTeUbB/Df7JixDGbGnj3...
172: "Optimal k by Silhouette: 2, Selected: 2\n"
181: "    gmm = GaussianMixture(n_components=k, covariance_type='full', n_init=5, random_state=42)\n",
183: "    sil = silhouette_score(X_regime, labels)\n",
184: "    db = davies_bouldin_score(X_regime, labels)\n",
185: "    ch = calinski_harabasz_score(X_regime, labels)\n",
187: "                      'silhouette': sil, 'davies_bouldin': db, 'calinski_harabasz': ch})\n",
188: "    print(f'  k={k}: BIC={gmm.bic(X_regime):.0f}, Silhouette={sil:.4f}, DB={db:.4f}')\n",
198: "axes[1].plot(list(k_range), results_k_df['silhouette'], 'g-o')\n",
199: "axes[1].set_xlabel('k'); axes[1].set_ylabel('Silhouette')\n",
200: "axes[1].set_title('Silhouette Score (higher = better)')\n",
202: "axes[2].plot(list(k_range), results_k_df['davies_bouldin'], 'm-o')\n",
203: "axes[2].set_xlabel('k'); axes[2].set_ylabel('Davies-Bouldin')\n",
204: "axes[2].set_title('Davies-Bouldin (lower = better)')\n",
210: "best_k = int(results_k_df.loc[results_k_df['silhouette'].idxmax(), 'k'])\n",
212: "print(f'\\nOptimal k by Silhouette: {best_k}, Selected: {REGIME_K}')"
232: "  Silhouette: 0.3400, DB: 1.4875, CH: 1343.02\n",
250: "gmm = GaussianMixture(n_components=REGIME_K, covariance_type='full', n_init=10, random_state=42)\n",
254: "gmm_sil = silhouette_score(X_regime, gmm_labels)\n",
255: "gmm_db = davies_bouldin_score(X_regime, gmm_labels)\n",
256: "gmm_ch = calinski_harabasz_score(X_regime, gmm_labels)\n",
259: "print(f'  Silhouette: {gmm_sil:.4f}, DB: {gmm_db:.4f}, CH: {gmm_ch:.2f}')\n",
301: "GMM Stability — Mean ARI: 1.0000, Min: 1.0000, Max: 1.0000\n"
306: "# GMM Stability\n",
308: "gmm_ari = []\n",
309: "all_gmm = [GaussianMixture(n_components=REGIME_K, covariance_type='full', n_init=10, random_state=s).fit_predict(X_regime) for s in seeds]\n",
312: "        gmm_ari.append(adjusted_rand_score(all_gmm[i], all_gmm[j]))\n",
313: "gmm_stability = np.mean(gmm_ari)\n",
314: "print(f'GMM Stability — Mean ARI: {gmm_stability:.4f}, Min: {np.min(gmm_ari):.4f}, Max: {np.max(gmm_ari):.4f}')"
334: "  Silhouette: 0.2507, DB: 1.6978, CH: 1009.22\n",
357: "hmm = GaussianHMM(n_components=REGIME_K, covariance_type='full', n_iter=200, random_state=42, tol=1e-4)\n",
362: "hmm_sil = silhouette_score(X_regime, hmm_labels)\n",
363: "hmm_db = davies_bouldin_score(X_regime, hmm_labels)\n",
364: "hmm_ch = calinski_harabasz_score(X_regime, hmm_labels)\n",
367: "print(f'  Silhouette: {hmm_sil:.4f}, DB: {hmm_db:.4f}, CH: {hmm_ch:.2f}')\n",
391: "HMM Stability — Mean ARI: 0.9107, Min: 0.7767, Max: 1.0000\n"
396: "# HMM Stability\n",
397: "hmm_ari = []\n",
400: "        h1 = GaussianHMM(n_components=REGIME_K, covariance_type='full', n_iter=200, random_state=seeds[i]).fit(X_regime)\n",
401: "        h2 = GaussianHMM(n_components=REGIME_K, covariance_type='full', n_iter=200, random_state=seeds[j]).fit(X_regime)\n",
402: "        hmm_ari.append(adjusted_rand_score(h1.predict(X_regime), h2.predict(X_regime)))\n",
403: "hmm_stability = np.mean(hmm_ari)\n",
404: "print(f'HMM Stability — Mean ARI: {hmm_stability:.4f}, Min: {np.min(hmm_ari):.4f}, Max: {np.max(hmm_ari):.4f}')"
411: "## 1.4 Regime Comparison & Selection"
424: "        Silhouette  0.3400  0.2507    GMM\n",
425: "    Davies-Bouldin  1.4875  1.6978    GMM\n",
426: " Calinski-Harabasz 1343.02 1009.22    GMM\n",
427: "   Stability (ARI)  1.0000  0.9107    GMM\n",
433: "# Comparison table\n",
435: "    'Metric': ['Silhouette', 'Davies-Bouldin', 'Calinski-Harabasz', 'Stability (ARI)', 'Regime Persistence'],\n",
436: "    'GMM': [f'{gmm_sil:.4f}', f'{gmm_db:.4f}', f'{gmm_ch:.2f}', f'{gmm_stability:.4f}', 'No'],\n",
437: "    'HMM': [f'{hmm_sil:.4f}', f'{hmm_db:.4f}', f'{hmm_ch:.2f}', f'{hmm_stability:.4f}', 'Yes'],\n",
442: "        'GMM' if gmm_stability > hmm_stability else 'HMM',\n",
447: "comp.to_csv(METRICS_DIR / 'regime_model_comparison.csv', index=False)"
496: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjUAAASlCAYAAADgeltjAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3Qd81PX9P/DX7bvcXTaBEEI...
535: "plt.savefig(FIGURES_DIR / 'regime_comparison_timeline.png', dpi=DPI, bbox_inches='tight')\n",
546: "image/png": "iVBORw0KGgoAAAANSUhEUgAABTsAAAHqCAYAAADLZ5rPAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAb79JREFUeJzt3Qd4U+X3wPFzC7SUPcoGmSI...
591: "gmm_score = (gmm_sil * 2) - (gmm_db * 0.5) + (gmm_stability * 1)\n",
592: "hmm_score = (hmm_sil * 2) - (hmm_db * 0.5) + (hmm_stability * 1) + 0.2\n",
606: "regime_output.to_parquet(PROCESSED_DIR / 'regime_assignments.parquet')\n",
622: "5. **StandardScaler for all models**: Tree models don't strictly need it, but it prevents numeric instability."
644: "  roc_21                    — redundant\n",
682: "    'roc_21',            # overlaps with target window\n",
773: "  11. roc_10                        \n",
854: "  Fold 1: Acc=0.4474, F1=0.5655, AUC=0.4758\n",
855: "  Fold 2: Acc=0.5307, F1=0.5804, AUC=0.5277\n",
856: "  Fold 3: Acc=0.5833, F1=0.7112, AUC=0.4741\n",
857: "  Fold 4: Acc=0.6096, F1=0.7390, AUC=0.3981\n",
858: "  Fold 5: Acc=0.6754, F1=0.7849, AUC=0.6894\n",
861: "  Fold 1: Acc=0.4474, F1=0.6182, AUC=0.4449\n",
862: "  Fold 2: Acc=0.5658, F1=0.6877, AUC=0.4899\n",
863: "  Fold 3: Acc=0.5965, F1=0.7444, AUC=0.4523\n",
864: "  Fold 4: Acc=0.6228, F1=0.7456, AUC=0.4544\n",
865: "  Fold 5: Acc=0.6184, F1=0.7507, AUC=0.5888\n",
868: "  Fold 1: Acc=0.4474, F1=0.6182, AUC=0.4876\n",
869: "  Fold 2: Acc=0.5877, F1=0.7360, AUC=0.4916\n",
870: "  Fold 3: Acc=0.6184, F1=0.7629, AUC=0.5040\n",
871: "  Fold 4: Acc=0.6404, F1=0.7807, AUC=0.4339\n",
872: "  Fold 5: Acc=0.6447, F1=0.7781, AUC=0.5762\n",
875: "  Fold 1: Acc=0.4474, F1=0.6182, AUC=0.6178\n",
876: "  Fold 2: Acc=0.5614, F1=0.6914, AUC=0.4831\n",
877: "  Fold 3: Acc=0.6140, F1=0.7609, AUC=0.4421\n",
878: "  Fold 4: Acc=0.6360, F1=0.7763, AUC=0.4759\n",
879: "  Fold 5: Acc=0.6009, F1=0.7437, AUC=0.4500\n",
901: "        random_state=42, use_label_encoder=False, eval_metric='logloss', verbosity=0\n",
933: "        acc = accuracy_score(y_te, y_pred)\n",
934: "        prec = precision_score(y_te, y_pred, zero_division=0)\n",
935: "        rec = recall_score(y_te, y_pred, zero_division=0)\n",
936: "        f1 = f1_score(y_te, y_pred, zero_division=0)\n",
937: "        try: auc = roc_auc_score(y_te, y_prob)\n",
938: "        except: auc = 0.5\n",
940: "        all_results[name].append({'fold': fi+1, 'accuracy': acc, 'precision': prec,\n",
941: "                                   'recall': rec, 'f1': f1, 'auc_roc': auc})\n",
943: "        print(f'  Fold {fi+1}: Acc={acc:.4f}, F1={f1:.4f}, AUC={auc:.4f}')\n",
952: "## 2.1 Signal Model Comparison"
964: "Signal Model Comparison (Walk-Forward CV):\n",
965: "              Model        Accuracy Precision Recall     F1         AUC-ROC\n",
979: "        'Accuracy': f\"{rdf['accuracy'].mean():.4f} ± {rdf['accuracy'].std():.4f}\",\n",
980: "        'Precision': f\"{rdf['precision'].mean():.4f}\",\n",
981: "        'Recall': f\"{rdf['recall'].mean():.4f}\",\n",
982: "        'F1': f\"{rdf['f1'].mean():.4f}\",\n",
983: "        'AUC-ROC': f\"{rdf['auc_roc'].mean():.4f} ± {rdf['auc_roc'].std():.4f}\",\n",
987: "print('Signal Model Comparison (Walk-Forward CV):')\n",
989: "summary_df.to_csv(METRICS_DIR / 'signal_model_comparison.csv', index=False)"
999: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjUAAAHqCAYAAABMTMx9AAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3Qd0VNXWB/D/9EnvpNATeg1...
1009: "# ─── COMPARISON PLOTS ────────────────────────────────────────\n",
1016: "    axes[0].plot(rdf['fold'], rdf['accuracy'], '-o', label=name, color=cm[idx])\n",
1017: "axes[0].set_xlabel('Fold'); axes[0].set_ylabel('Accuracy')\n",
1018: "axes[0].set_title('Accuracy per Fold'); axes[0].legend(fontsize=8)\n",
1023: "    axes[1].plot(rdf['fold'], rdf['auc_roc'], '-o', label=name, color=cm[idx])\n",
1024: "axes[1].set_xlabel('Fold'); axes[1].set_ylabel('AUC-ROC')\n",
1025: "axes[1].set_title('AUC-ROC per Fold'); axes[1].legend(fontsize=8)\n",
1028: "metrics_bar = ['accuracy', 'f1', 'auc_roc']\n",
1036: "axes[2].set_xticklabels(['Accuracy', 'F1', 'AUC-ROC'])\n",
1040: "plt.savefig(FIGURES_DIR / 'signal_model_comparison.png', dpi=DPI, bbox_inches='tight')\n",
1051: "image/png": "iVBORw0KGgoAAAANSUhEUgAAAwkAAAMWCAYAAAC6G8rCAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3Qd803X+P/BXRts0XXRR9qb...
1061: "# ─── ROC CURVES ──────────────────────────────────────────────\n",
1067: "        auc = roc_auc_score(yt, yp)\n",
1068: "        RocCurveDisplay.from_predictions(yt, yp, name=f'{name} (AUC={auc:.3f})',\n",
1072: "ax.set_title('ROC Curves — Signal Model Candidates')\n",
1075: "plt.savefig(FIGURES_DIR / 'signal_roc_curves.png', dpi=DPI, bbox_inches='tight')\n",
1086: "image/png": "iVBORw0KGgoAAAANSUhEUgAABuwAAAGdCAYAAAD5b1WHAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAreVJREFUeJzs3Qd4FFXXwPGzkQ7SQpFApPc...
1126: "image/png": "iVBORw0KGgoAAAANSUhEUgAAA90AAAMWCAYAAADs4eXxAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAnbZJREFUeJzs3QmcjeX///EPY2eMrNlClCi...
1198: "Regime                    N      Acc       F1      AUC\n",
1218: "print(f'{\"Regime\":20s} {\"N\":>6s} {\"Acc\":>8s} {\"F1\":>8s} {\"AUC\":>8s}')\n",
1226: "    acc = accuracy_score(y_te_final[mask], y_pred_final[mask])\n",
1227: "    f1 = f1_score(y_te_final[mask], y_pred_final[mask], zero_division=0)\n",
1228: "    try: auc = roc_auc_score(y_te_final[mask], lgbm_imp.predict_proba(X_te_final[mask])[:, 1])\n",
1229: "    except: auc = 0.5\n",
1230: "    regime_perf.append({'Regime': rn, 'N': int(mask.sum()), 'Accuracy': acc, 'F1': f1, 'AUC': auc})\n",
1231: "    print(f'{rn:20s} {mask.sum():>6d} {acc:>8.4f} {f1:>8.4f} {auc:>8.4f}')\n",
1259: "  Silhouette: 0.3400, DB: 1.4875, Stability: 1.0000\n",
1264: "  AUC-ROC: 0.5130 (mean across 5 folds)\n",
1265: "  Accuracy: 0.5693\n",
1266: "  F1: 0.6762\n",
1273: "best_name = max(all_results.items(), key=lambda x: pd.DataFrame(x[1])['auc_roc'].mean())\n",
1275: "best_auc = pd.DataFrame(best_name[1])['auc_roc'].mean()\n",
1285: "st = hmm_stability if selected_regime == 'HMM' else gmm_stability\n",
1286: "print(f'  Silhouette: {s:.4f}, DB: {d:.4f}, Stability: {st:.4f}')\n",
1290: "print(f'  AUC-ROC: {best_auc:.4f} (mean across {len(folds)} folds)')\n",
1291: "print(f'  Accuracy: {best_df[\"accuracy\"].mean():.4f}')\n",
1292: "print(f'  F1: {best_df[\"f1\"].mean():.4f}')\n",
1324: "    'regime_silhouette': float(s), 'regime_db': float(d),\n",
1326: "    'signal_auc': float(best_auc), 'signal_horizon': HORIZON,\n",
1344: "image/png": "iVBORw0KGgoAAAANSUhEUgAABjUAAATNCAYAAAAE3dZUAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjgsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvwVt1zgAAAAlwSFlzAAAPYQAAD2EBqD+naQABAABJREFUeJzs3QWUHGXWxvGnZVzjriQhBgE...
1366: "# AUC comparison\n",
1367: "aucs = [pd.DataFrame(all_results[n])['auc_roc'].mean() for n in model_names]\n",
1370: "axes[0, 1].bar(short, aucs, color=bc)\n",
1372: "axes[0, 1].set_ylabel('AUC-ROC'); axes[0, 1].set_title(f'Signal: {best_signal_name}')\n",
1373: "for i, v in enumerate(aucs): axes[0, 1].text(i, v+0.005, f'{v:.3f}', ha='center')\n",
1385: "    axes[1, 1].bar(x-0.15, [r['Accuracy'] for r in regime_perf], 0.3, label='Accuracy', color='#3498db')\n",
1386: "    axes[1, 1].bar(x+0.15, [r['F1'] for r in regime_perf], 0.3, label='F1', color='#e74c3c')\n",
1440: "GMM: Sil=0.3400, DB=1.4875, CH=1343.02, Stability=1.0000, Trans=128\n",
1442: "HMM: Sil=0.2507, DB=1.6978, CH=1009.22, Stability=0.9107, Trans=46\n",
1454: "    F1: Acc=0.4474 F1=0.5655 AUC=0.4758\n",
1455: "    F2: Acc=0.5307 F1=0.5804 AUC=0.5277\n",
1456: "    F3: Acc=0.5833 F1=0.7112 AUC=0.4741\n",
1457: "    F4: Acc=0.6096 F1=0.7390 AUC=0.3981\n",
1458: "    F5: Acc=0.6754 F1=0.7849 AUC=0.6894\n",
1459: "    MEAN: Acc=0.5693 F1=0.6762 AUC=0.5130\n",
1462: "    F1: Acc=0.4474 F1=0.6182 AUC=0.4449\n",
1463: "    F2: Acc=0.5658 F1=0.6877 AUC=0.4899\n",
1464: "    F3: Acc=0.5965 F1=0.7444 AUC=0.4523\n",
1465: "    F4: Acc=0.6228 F1=0.7456 AUC=0.4544\n",
1466: "    F5: Acc=0.6184 F1=0.7507 AUC=0.5888\n",
1467: "    MEAN: Acc=0.5702 F1=0.7093 AUC=0.4861\n",
1470: "    F1: Acc=0.4474 F1=0.6182 AUC=0.4876\n",
1471: "    F2: Acc=0.5877 F1=0.7360 AUC=0.4916\n",
1472: "    F3: Acc=0.6184 F1=0.7629 AUC=0.5040\n",
1473: "    F4: Acc=0.6404 F1=0.7807 AUC=0.4339\n",
1474: "    F5: Acc=0.6447 F1=0.7781 AUC=0.5762\n",
1475: "    MEAN: Acc=0.5877 F1=0.7352 AUC=0.4987\n",
1478: "    F1: Acc=0.4474 F1=0.6182 AUC=0.6178\n",
1479: "    F2: Acc=0.5614 F1=0.6914 AUC=0.4831\n",
1480: "    F3: Acc=0.6140 F1=0.7609 AUC=0.4421\n",
1481: "    F4: Acc=0.6360 F1=0.7763 AUC=0.4759\n",
1482: "    F5: Acc=0.6009 F1=0.7437 AUC=0.4500\n",
1483: "    MEAN: Acc=0.5719 F1=0.7181 AUC=0.4938\n",
1504: "         Regime   N  Accuracy       F1      AUC\n",
1509: "['cpi', 'fed_funds_rate', 'gold_equity_ratio', 'industrial_production', 'log_ret_10d', 'log_ret_21d', 'mean_ret_21d', 'mean_ret_63d', 'parkinson_vol_21d', 'roc_21', 'treasury_10y', 'treasury_2y', 'volatility_5d', 'vo...
1512: "Regime: GMM (k=2), Signal: LightGBM (AUC=0.5130)\n"
1526: "print(f\"GMM: Sil={gmm_sil:.4f}, DB={gmm_db:.4f}, CH={gmm_ch:.2f}, Stability={gmm_stability:.4f}, Trans={np.sum(np.diff(gmm_labels)!=0)}\")\n",
1528: "print(f\"HMM: Sil={hmm_sil:.4f}, DB={hmm_db:.4f}, CH={hmm_ch:.2f}, Stability={hmm_stability:.4f}, Trans={np.sum(np.diff(hmm_labels)!=0)}\")\n",
1539: "        print(f\"    F{r['fold']}: Acc={r['accuracy']:.4f} F1={r['f1']:.4f} AUC={r['auc_roc']:.4f}\")\n",
1540: "    print(f\"    MEAN: Acc={rdf['accuracy'].mean():.4f} F1={rdf['f1'].mean():.4f} AUC={rdf['auc_roc'].mean():.4f}\")\n",
1552: "best_n = max(all_results.items(), key=lambda x: pd.DataFrame(x[1])['auc_roc'].mean())\n",
1553: "print(f\"Regime: {selected_regime} (k={REGIME_K}), Signal: {best_n[0]} (AUC={pd.DataFrame(best_n[1])['auc_roc'].mean():.4f})\")"
1577: "  F1: Acc=0.4278 F1=0.5992 AUC=0.4391\n",
1578: "  F2: Acc=0.6222 F1=0.7671 AUC=0.5366\n",
1579: "  F3: Acc=0.5944 F1=0.7420 AUC=0.4572\n",
1580: "  F4: Acc=0.6167 F1=0.7629 AUC=0.4495\n",
1581: "  F5: Acc=0.6500 F1=0.7879 AUC=0.6067\n",
1584: "  F1: Acc=0.4278 F1=0.5992 AUC=0.4955\n",
1585: "  F2: Acc=0.6278 F1=0.7713 AUC=0.4828\n",
1586: "  F3: Acc=0.5944 F1=0.7456 AUC=0.4095\n",
1587: "  F4: Acc=0.6167 F1=0.7629 AUC=0.4724\n",
1588: "  F5: Acc=0.6500 F1=0.7879 AUC=0.5858\n",
1591: "  F1: Acc=0.4278 F1=0.5992 AUC=0.4491\n",
1592: "  F2: Acc=0.6222 F1=0.7671 AUC=0.5131\n",
1593: "  F3: Acc=0.5944 F1=0.7439 AUC=0.5259\n",
1594: "  F4: Acc=0.6111 F1=0.7586 AUC=0.4463\n",
1595: "  F5: Acc=0.6500 F1=0.7879 AUC=0.6148\n",
1598: "  F1: Acc=0.4278 F1=0.5992 AUC=0.5177\n",
1599: "  F2: Acc=0.6278 F1=0.7713 AUC=0.5159\n",
1600: "  F3: Acc=0.5944 F1=0.7456 AUC=0.4693\n",
1601: "  F4: Acc=0.6111 F1=0.7586 AUC=0.5565\n",
1602: "  F5: Acc=0.6444 F1=0.7838 AUC=0.4933\n",
1606: "LightGBM              : Acc=0.5822  F1=0.7318  AUC=0.4978  (min AUC=0.4391)\n",
1607: "XGBoost               : Acc=0.5833  F1=0.7334  AUC=0.4892  (min AUC=0.4095)\n",
1608: "Random Forest         : Acc=0.5811  F1=0.7313  AUC=0.5099  (min AUC=0.4463)\n",
1609: "Logistic Regression   : Acc=0.5811  F1=0.7317  AUC=0.5105  (min AUC=0.4693)\n"
1707: "# ─── CANDIDATES (heavily regularized) ────────────────────────\n",
1719: "        random_state=42, use_label_encoder=False, eval_metric='logloss', verbosity=0\n",
1747: "        acc = accuracy_score(y_te, y_pred)\n",
1748: "        f1 = f1_score(y_te, y_pred, zero_division=0)\n",
1749: "        try: auc = roc_auc_score(y_te, y_prob)\n",
1750: "        except: auc = 0.5\n",
1751: "        prec = precision_score(y_te, y_pred, zero_division=0)\n",
1752: "        rec = recall_score(y_te, y_pred, zero_division=0)\n",
1754: "        all_results[name].append({'fold': fi+1, 'accuracy': acc, 'precision': prec,\n",
1755: "                                   'recall': rec, 'f1': f1, 'auc_roc': auc})\n",
1757: "        print(f'  F{fi+1}: Acc={acc:.4f} F1={f1:.4f} AUC={auc:.4f}')\n",
1763: "    print(f\"{name:22s}: Acc={rdf['accuracy'].mean():.4f}  F1={rdf['f1'].mean():.4f}  AUC={rdf['auc_roc'].mean():.4f}  (min AUC={rdf['auc_roc'].min():.4f})\")"
```

## Parquet Data Inventory

- `app/data/features/features_all.parquet`: 15704 rows x 45 cols
- `app/data/features/features_btc_usd.parquet`: 3930 rows x 43 cols
- `app/data/features/features_iwm.parquet`: 3930 rows x 43 cols
- `app/data/features/features_qqq.parquet`: 3918 rows x 43 cols
- `app/data/features/features_spy.parquet`: 3926 rows x 42 cols
- `app/data/processed/outlier_flags.parquet`: 4173 rows x 4 cols
- `app/data/processed/regime_assignments.parquet`: 3926 rows x 4 cols
- `app/data/processed/universe.parquet`: 4173 rows x 38 cols
- `app/data/processed/universe_raw_snapshot.parquet`: 6616 rows x 38 cols
- `app/data/raw/fama_french.parquet`: 5283 rows x 4 cols
- `app/data/raw/fred_macro.parquet`: 7719 rows x 7 cols
- `app/data/raw/ohlcv_btc_usd.parquet`: 4173 rows x 5 cols
- `app/data/raw/ohlcv_gld.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_iwm.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_qqq.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_spy.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_uso.parquet`: 4996 rows x 5 cols
- `app/data/raw/ohlcv_vix.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_xle.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_xlf.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_xlk.parquet`: 5315 rows x 5 cols
- `app/data/raw/ohlcv_xlv.parquet`: 5315 rows x 5 cols

const BASE = typeof window === "undefined"
  ? "http://localhost:8000/api"
  : "/api";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export interface Signal {
  date: string;
  signal: string;
  signal_prob: number;
  exposure: number;
  risk_score: number;
  regime: string;
  risk_flags: string;
  asset_ret: number;
}

export interface Metrics {
  asset: string;
  sized_sharpe: number;
  bh_sharpe: number;
  cum_return_sized_pct: number;
  cum_return_bh_pct: number;
  max_dd_sized_pct: number;
  max_dd_bh_pct: number;
  avg_exposure_pct: number;
  annualized_vol_pct: number;
  turnover_annual: number;
  win_rate_pct: number;
  avg_var95_pct: number;
  n_test_days: number;
  test_period: string;
}

export interface EquityPoint {
  date: string;
  strategy: number;
  buyhold: number;
}

export interface RegimePoint {
  date: string;
  regime: number;
  exposure: number;
}

export interface DrawdownPoint {
  date: string;
  strategy: number;
  buyhold: number;
}

export interface PortfolioSummary {
  sharpe: number;
  total_return: number;
  max_drawdown: number;
  annualized_vol: number;
  allocation: Record<string, number>;
  equity_curve: { date: string; portfolio: number }[];
  n_days: number;
  start_date: string;
  end_date: string;
}

export interface SignalHistory {
  date: string;
  signal: string;
  exposure: number;
  risk_score: number;
  regime: string;
  daily_return: number;
}

export const fetchCurrentSignals = () =>
  fetchJSON<Record<string, Signal>>("/signals/current");

export const fetchAllMetrics = () =>
  fetchJSON<Record<string, Metrics>>("/metrics");

export const fetchMetrics = (asset: string) =>
  fetchJSON<Metrics>(`/metrics/${asset}`);

export const fetchEquityCurve = (asset: string) =>
  fetchJSON<EquityPoint[]>(`/backtest/${asset}/equity`);

export const fetchDrawdown = (asset: string) =>
  fetchJSON<DrawdownPoint[]>(`/backtest/${asset}/drawdown`);

export const fetchRegime = (asset: string) =>
  fetchJSON<RegimePoint[]>(`/backtest/${asset}/regime`);

export const fetchPortfolioSummary = () =>
  fetchJSON<PortfolioSummary>("/portfolio/summary");

export const fetchSignalHistory = (asset: string, days = 30) =>
  fetchJSON<SignalHistory[]>(`/signals/${asset}/history?days=${days}`);


export interface LiveSignal {
  asset: string;
  date: string;
  price: number;
  daily_change_pct: number;
  signal: string;
  portfolio_weight_pct: number;
  exposure_pct: number;
  risk_score: number;
  regime: string;
  regime_confidence: number;
  realized_vol_pct: number;
  risk_flags: string[];
  var_95_pct: number;
  kelly_fraction: number;
  above_sma50: boolean;
  rsi_14: number;
  vol_filter_pass: boolean;
}

export interface LiveSignalData {
  generated_at: string;
  market_date: string;
  signals: Record<string, LiveSignal>;
}

export const fetchLiveSignals = () =>
  fetchJSON<LiveSignalData>("/signals/live");

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  publisher: string;
  date: string;
  url: string;
  thumbnail: string;
  ticker: string;
  asset_label: string;
}

export interface NewsData {
  articles: NewsArticle[];
  fetched_at: string;
}

export const fetchNews = () => fetchJSON<NewsData>("/news");
export const fetchNewsShuffle = () => fetchJSON<NewsData>("/news?shuffle=true");

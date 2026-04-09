import Link from "next/link";
import Navbar from "@/components/Navbar";
import RefreshButton from "@/components/RefreshButton";
import MarketNews from "@/components/MarketNews";
import { fetchLiveSignals, fetchNews } from "@/lib/api";
import type { LiveSignal, NewsArticle } from "@/lib/api";

const COLORS: Record<string, string> = {
  SPY: "#22c55e", QQQ: "#3b82f6", IWM: "#a855f7", BTC: "#f59e0b",
};
const NAMES: Record<string, string> = {
  SPY: "S&P 500", QQQ: "Nasdaq 100", IWM: "Russell 2000", BTC: "Bitcoin",
};

function formatPrice(price: number, asset: string) {
  return asset === "BTC"
    ? `$${price.toLocaleString("en-US", { maximumFractionDigits: 0 })}`
    : `$${price.toFixed(2)}`;
}

function RiskBar({ score }: { score: number }) {
  const color = score <= 30 ? "#22c55e" : score <= 60 ? "#f59e0b" : "#ef4444";
  const label = score <= 30 ? "LOW" : score <= 60 ? "MODERATE" : "HIGH";
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs" style={{ color: "var(--muted)" }}>Risk</span>
        <span className="text-xs font-semibold" style={{ color }}>{label} ({score}/100)</span>
      </div>
      <div className="h-2 rounded-full" style={{ background: "var(--card-border)" }}>
        <div className="h-full rounded-full transition-all" style={{ width: `${score}%`, background: color }} />
      </div>
    </div>
  );
}

function SignalCard({ asset, sig }: { asset: string; sig: LiveSignal }) {
  const color = COLORS[asset];
  const isLong = sig.signal === "LONG";

  return (
    <div className="rounded-xl border" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      {/* Header */}
      <div className="p-5 border-b" style={{ borderColor: "var(--card-border)" }}>
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold" style={{ color }}>{asset}</h3>
              <span className="text-xs" style={{ color: "var(--muted)" }}>{NAMES[asset]}</span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-xl font-bold font-mono">{formatPrice(sig.price, asset)}</p>
            <p className={`text-sm font-mono ${sig.daily_change_pct >= 0 ? "text-[#22c55e]" : "text-[#ef4444]"}`}>
              {sig.daily_change_pct > 0 ? "+" : ""}{sig.daily_change_pct}%
            </p>
          </div>
        </div>
      </div>

      {/* Signal Action */}
      <div className="p-5 border-b" style={{ borderColor: "var(--card-border)" }}>
        <div className={`rounded-lg p-5 text-center ${
          isLong ? "bg-green-950/40 border border-green-800/30" : "bg-neutral-900/40 border border-neutral-700/30"
        }`}>
          <p className={`text-2xl font-bold mb-1 ${isLong ? "text-[#22c55e]" : "text-neutral-500"}`}>
            {isLong ? "GO LONG" : "STAY FLAT"}
          </p>
          {isLong ? (
            <p className="text-sm">
              Allocate <span className="font-bold text-[#22c55e]">{sig.exposure_pct}%</span> of portfolio
              <span style={{ color: "var(--muted)" }}> (max {sig.portfolio_weight_pct || 25}% for this asset)</span>
            </p>
          ) : (
            <p className="text-sm" style={{ color: "var(--muted)" }}>Do not hold — entry conditions not met</p>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="p-5 space-y-4">
        {/* Regime */}
        <div className="flex items-center justify-between">
          <span className="text-sm" style={{ color: "var(--muted)" }}>Market Regime</span>
          <div className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${sig.regime === "NORMAL" ? "bg-[#22c55e]" : "bg-[#ef4444] animate-pulse"}`} />
            <span className="font-semibold text-sm">{sig.regime}</span>
            <span className="text-xs" style={{ color: "var(--muted)" }}>({sig.regime_confidence}%)</span>
          </div>
        </div>

        {/* Risk Bar */}
        <RiskBar score={sig.risk_score} />

        {/* Key Numbers */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          <div className="rounded-lg p-3" style={{ background: "var(--background)" }}>
            <p className="text-xs mb-1" style={{ color: "var(--muted)" }}>RSI (14)</p>
            <p className={`text-lg font-bold font-mono ${sig.rsi_14 > 40 ? "text-[#22c55e]" : "text-[#ef4444]"}`}>
              {sig.rsi_14}
            </p>
          </div>
          <div className="rounded-lg p-3" style={{ background: "var(--background)" }}>
            <p className="text-xs mb-1" style={{ color: "var(--muted)" }}>Volatility (21d)</p>
            <p className={`text-lg font-bold font-mono ${sig.realized_vol_pct > 25 ? "text-[#ef4444]" : "text-[#22c55e]"}`}>
              {sig.realized_vol_pct}%
            </p>
          </div>
          <div className="rounded-lg p-3" style={{ background: "var(--background)" }}>
            <p className="text-xs mb-1" style={{ color: "var(--muted)" }}>VaR 95%</p>
            <p className="text-lg font-bold font-mono text-[#ef4444]">{sig.var_95_pct}%</p>
          </div>
          <div className="rounded-lg p-3" style={{ background: "var(--background)" }}>
            <p className="text-xs mb-1" style={{ color: "var(--muted)" }}>Allocation</p>
            <p className={`text-lg font-bold font-mono ${sig.exposure_pct > 0 ? "text-[#22c55e]" : ""}`}>
              {sig.exposure_pct}%
            </p>
          </div>
        </div>

        {/* Entry Conditions */}
        <div className="pt-2">
          <p className="text-xs font-medium mb-2" style={{ color: "var(--muted)" }}>Entry Conditions</p>
          <div className="grid grid-cols-3 gap-2">
            <div className={`rounded-lg p-2 text-center text-xs font-medium border ${
              sig.above_sma50
                ? "bg-green-950/30 border-green-800/30 text-[#22c55e]"
                : "bg-red-950/30 border-red-800/30 text-[#ef4444]"
            }`}>
              {sig.above_sma50 ? "PASS" : "FAIL"}
              <br />
              <span style={{ color: "var(--muted)" }}>Trend (SMA-50)</span>
            </div>
            <div className={`rounded-lg p-2 text-center text-xs font-medium border ${
              sig.rsi_14 > 40
                ? "bg-green-950/30 border-green-800/30 text-[#22c55e]"
                : "bg-red-950/30 border-red-800/30 text-[#ef4444]"
            }`}>
              {sig.rsi_14 > 40 ? "PASS" : "FAIL"}
              <br />
              <span style={{ color: "var(--muted)" }}>RSI &gt; 40</span>
            </div>
            <div className={`rounded-lg p-2 text-center text-xs font-medium border ${
              sig.vol_filter_pass
                ? "bg-green-950/30 border-green-800/30 text-[#22c55e]"
                : "bg-red-950/30 border-red-800/30 text-[#ef4444]"
            }`}>
              {sig.vol_filter_pass ? "PASS" : "FAIL"}
              <br />
              <span style={{ color: "var(--muted)" }}>Volatility</span>
            </div>
          </div>
        </div>

        {/* Risk Flags */}
        {sig.risk_flags.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {sig.risk_flags.map((flag) => (
              <span key={flag} className="text-xs px-2 py-1 rounded border bg-red-950/30 border-red-800/30 text-[#ef4444]">
                {flag.replace(/_/g, " ")}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default async function SignalsPage() {
  let liveData = null;
  let newsArticles: NewsArticle[] = [];
  try {
    const [live, newsData] = await Promise.all([
      fetchLiveSignals(),
      fetchNews().catch(() => ({ articles: [] })),
    ]);
    liveData = live;
    newsArticles = newsData.articles || [];
  } catch {
    // API offline
  }

  const hasLive = liveData !== null;
  const signals = hasLive ? liveData!.signals : null;

  return (
    <div className="min-h-screen" style={{ background: "var(--background)", color: "var(--foreground)" }}>
      <Navbar extra={
        hasLive ? (
          <span className="flex items-center gap-1.5 text-xs" style={{ color: "var(--muted)" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-[#22c55e] animate-pulse" />
            {liveData!.market_date}
          </span>
        ) : undefined
      } />

      <main className="max-w-6xl mx-auto px-8 py-10">
        {!hasLive ? (
          <div className="text-center py-20">
            <h2 className="text-xl font-bold mb-2">API Offline</h2>
            <p style={{ color: "var(--muted)" }}>
              Start the backend and run daily signals first.
            </p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold">Live Signals</h1>
                <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
                  Market close {liveData!.market_date} &middot;{" "}
                  Generated {new Date(liveData!.generated_at).toLocaleString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <RefreshButton />
                <Link href="/learn" className="text-sm px-4 py-2 rounded-lg border transition-colors hover:border-[#22c55e] hover:text-[#22c55e]" style={{ borderColor: "var(--card-border)" }}>
                  What do these mean?
                </Link>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {signals && Object.entries(signals).map(([asset, sig]) => (
                <SignalCard key={asset} asset={asset} sig={sig} />
              ))}
            </div>

            <MarketNews initial={newsArticles} />

            {/* Disclaimer */}
            <p className="text-center text-xs mt-10 py-4 border-t" style={{ borderColor: "var(--card-border)", color: "var(--muted)" }}>
              Signals are generated from market data after close. Not financial advice.
              Always do your own research. <Link href="/learn" className="underline">Learn how these signals work</Link>.
            </p>
          </>
        )}
      </main>
    </div>
  );
}

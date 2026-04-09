import { fetchCurrentSignals, fetchAllMetrics, fetchPortfolioSummary } from "@/lib/api";
import AssetCard from "@/components/AssetCard";
import PositionsTable from "@/components/PositionsTable";
import PortfolioChart from "@/components/PortfolioChart";
import StatCard from "@/components/StatCard";

const ASSET_ORDER = ["SPY", "QQQ", "IWM", "BTC"];

export default async function Dashboard() {
  let signals, metrics, portfolio;

  try {
    [signals, metrics, portfolio] = await Promise.all([
      fetchCurrentSignals(),
      fetchAllMetrics(),
      fetchPortfolioSummary(),
    ]);
  } catch {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <h2 className="text-xl font-bold mb-2">API Offline</h2>
          <p style={{ color: "var(--muted)" }}>
            Start the backend: <code className="px-2 py-1 rounded text-sm" style={{ background: "var(--card)" }}>cd Backend && uvicorn api.main:app --port 8000</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
          {portfolio.start_date.slice(0, 10)} to {portfolio.end_date.slice(0, 10)}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Portfolio Sharpe" value={`+${portfolio.sharpe}`} color="text-[#22c55e]" />
        <StatCard label="Total Return" value={`+${portfolio.total_return}%`} color="text-[#22c55e]" />
        <StatCard label="Max Drawdown" value={`${portfolio.max_drawdown}%`} color="text-[#ef4444]" />
        <StatCard label="Annual Vol" value={`${portfolio.annualized_vol}%`} />
      </div>

      <PortfolioChart data={portfolio.equity_curve} />

      <div>
        <h2 className="text-lg font-semibold mb-3">Assets</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {ASSET_ORDER.map((asset) => (
            <AssetCard key={asset} asset={asset} signal={signals[asset]} metrics={metrics[asset]} />
          ))}
        </div>
      </div>

      <PositionsTable signals={signals} />
    </div>
  );
}

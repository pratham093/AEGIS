import { fetchMetrics, fetchEquityCurve, fetchRegime, fetchSignalHistory } from "@/lib/api";
import EquityCurve from "@/components/EquityCurve";
import MetricsPanel from "@/components/MetricsPanel";
import RegimeChart from "@/components/RegimeChart";

const VALID_ASSETS = ["spy", "qqq", "iwm", "btc"];

interface AssetPageProps {
  params: Promise<{ slug: string }>;
}

export default async function AssetPage({ params }: AssetPageProps) {
  const { slug } = await params;
  const asset = slug.toLowerCase();

  if (!VALID_ASSETS.includes(asset)) {
    return <div className="text-center py-20 text-[#737373]">Asset not found</div>;
  }

  let metrics, equity, regime, history;

  try {
    [metrics, equity, regime, history] = await Promise.all([
      fetchMetrics(asset),
      fetchEquityCurve(asset),
      fetchRegime(asset),
      fetchSignalHistory(asset, 60),
    ]);
  } catch {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-[#737373]">Failed to load data. Is the API running?</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{asset.toUpperCase()}</h1>
        <p className="text-[#737373] text-sm mt-1">{metrics.test_period}</p>
      </div>

      <MetricsPanel metrics={metrics} />
      <EquityCurve data={equity} asset={asset} />
      <RegimeChart data={regime} asset={asset} />

      <div className="rounded-xl border border-[#252525] bg-[#141414] overflow-hidden">
        <div className="px-5 py-4 border-b border-[#252525]">
          <h3 className="font-semibold">Recent Signals (60 days)</h3>
        </div>
        <div className="max-h-96 overflow-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-[#141414]">
              <tr className="text-[#737373] border-b border-[#252525]">
                <th className="text-left px-5 py-3 font-medium">Date</th>
                <th className="text-left px-5 py-3 font-medium">Signal</th>
                <th className="text-right px-5 py-3 font-medium">Exposure</th>
                <th className="text-left px-5 py-3 font-medium">Regime</th>
                <th className="text-right px-5 py-3 font-medium">Daily P&L</th>
              </tr>
            </thead>
            <tbody>
              {history.slice().reverse().map((row) => (
                <tr key={row.date} className="border-b border-[#1a1a1a] hover:bg-[#1a1a1a]">
                  <td className="px-5 py-2 font-mono text-xs">{row.date.slice(0, 10)}</td>
                  <td className="px-5 py-2">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                      row.signal === "LONG"
                        ? "bg-green-900/40 text-green-400"
                        : "bg-neutral-800 text-neutral-400"
                    }`}>
                      {row.signal}
                    </span>
                  </td>
                  <td className="px-5 py-2 text-right font-mono">{row.exposure}%</td>
                  <td className="px-5 py-2">
                    <span className="flex items-center gap-1.5">
                      <span className={`w-1.5 h-1.5 rounded-full ${row.regime === "NORMAL" ? "bg-green-400" : "bg-red-400"}`} />
                      <span className="text-xs">{row.regime}</span>
                    </span>
                  </td>
                  <td className={`px-5 py-2 text-right font-mono ${row.daily_return >= 0 ? "text-green-400" : "text-red-400"}`}>
                    {row.daily_return > 0 ? "+" : ""}{row.daily_return}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

"use client";
import Link from "next/link";
import type { Signal, Metrics } from "@/lib/api";

const COLORS: Record<string, string> = {
  SPY: "#22c55e",
  QQQ: "#3b82f6",
  IWM: "#a855f7",
  BTC: "#f59e0b",
};

interface AssetCardProps {
  asset: string;
  signal: Signal;
  metrics: Metrics;
}

export default function AssetCard({ asset, signal, metrics }: AssetCardProps) {
  const color = COLORS[asset] || "#fff";

  return (
    <Link href={`/dashboard/asset/${asset.toLowerCase()}`}>
      <div className="rounded-xl border p-5 transition-colors cursor-pointer"
        style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-bold" style={{ color }}>{asset}</h3>
          <span
            className={`text-xs font-semibold px-2 py-1 rounded ${
              signal.signal === "LONG"
                ? "bg-green-900/40 text-green-400"
                : "bg-neutral-800 text-neutral-400"
            }`}
          >
            {signal.signal}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <p className="text-[#737373]">Sharpe</p>
            <p className="font-semibold">{metrics.sized_sharpe > 0 ? "+" : ""}{metrics.sized_sharpe}</p>
          </div>
          <div>
            <p className="text-[#737373]">Exposure</p>
            <p className="font-semibold">{signal.exposure}%</p>
          </div>
          <div>
            <p className="text-[#737373]">Return</p>
            <p className={`font-semibold ${metrics.cum_return_sized_pct >= 0 ? "text-green-400" : "text-red-400"}`}>
              {metrics.cum_return_sized_pct > 0 ? "+" : ""}{metrics.cum_return_sized_pct}%
            </p>
          </div>
          <div>
            <p className="text-[#737373]">Max DD</p>
            <p className="font-semibold text-red-400">{metrics.max_dd_sized_pct}%</p>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${signal.regime === "NORMAL" ? "bg-green-400" : "bg-red-400"}`} />
          <span className="text-xs text-[#737373]">{signal.regime}</span>
          <span className="text-xs text-[#737373] ml-auto">Risk: {signal.risk_score}/100</span>
        </div>
      </div>
    </Link>
  );
}

"use client";
import type { Signal } from "@/lib/api";

const COLORS: Record<string, string> = {
  SPY: "#22c55e",
  QQQ: "#3b82f6",
  IWM: "#a855f7",
  BTC: "#f59e0b",
};

interface PositionsTableProps {
  signals: Record<string, Signal>;
}

export default function PositionsTable({ signals }: PositionsTableProps) {
  return (
    <div className="rounded-xl border overflow-hidden" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <div className="px-5 py-4 border-b" style={{ borderColor: "var(--card-border)" }}>
        <h3 className="font-semibold">Current Positions</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr style={{ borderBottom: "1px solid var(--card-border)", color: "var(--muted)" }}>
            <th className="text-left px-5 py-3 font-medium">Asset</th>
            <th className="text-left px-5 py-3 font-medium">Signal</th>
            <th className="text-right px-5 py-3 font-medium">Exposure</th>
            <th className="text-left px-5 py-3 font-medium">Regime</th>
            <th className="text-right px-5 py-3 font-medium">Risk Score</th>
            <th className="text-right px-5 py-3 font-medium">Daily P&L</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(signals).map(([asset, sig]) => (
            <tr key={asset} style={{ borderBottom: "1px solid var(--table-border)" }}>
              <td className="px-5 py-3 font-semibold" style={{ color: COLORS[asset] }}>{asset}</td>
              <td className="px-5 py-3">
                <span className={`text-xs font-semibold px-2 py-1 rounded ${
                  sig.signal === "LONG" ? "bg-green-900/40 text-green-400" : "bg-neutral-800/40 text-neutral-400"
                }`}>
                  {sig.signal}
                </span>
              </td>
              <td className="px-5 py-3 text-right font-mono">{sig.exposure}%</td>
              <td className="px-5 py-3">
                <span className="flex items-center gap-1.5">
                  <span className={`w-2 h-2 rounded-full ${sig.regime === "NORMAL" ? "bg-green-400" : "bg-red-400"}`} />
                  {sig.regime}
                </span>
              </td>
              <td className="px-5 py-3 text-right font-mono">{sig.risk_score}</td>
              <td className={`px-5 py-3 text-right font-mono ${sig.asset_ret >= 0 ? "text-[#22c55e]" : "text-[#ef4444]"}`}>
                {sig.asset_ret > 0 ? "+" : ""}{sig.asset_ret}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

"use client";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, Legend,
} from "recharts";
import type { EquityPoint } from "@/lib/api";

const COLORS: Record<string, string> = {
  SPY: "#22c55e",
  QQQ: "#3b82f6",
  IWM: "#a855f7",
  BTC: "#f59e0b",
};

interface EquityCurveProps {
  data: EquityPoint[];
  asset: string;
}

export default function EquityCurve({ data, asset }: EquityCurveProps) {
  const color = COLORS[asset.toUpperCase()] || "#22c55e";
  const sampled = data.filter((_, i) => i % 5 === 0 || i === data.length - 1);

  return (
    <div className="rounded-xl border p-5" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <h3 className="font-semibold mb-4">Equity Curve</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={sampled}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252525" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#737373", fontSize: 11 }}
            tickFormatter={(v) => v.slice(0, 7)}
            interval={Math.floor(sampled.length / 6)}
          />
          <YAxis tick={{ fill: "#737373", fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
          <Tooltip
            contentStyle={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }}
            labelStyle={{ color: "#999" }}
            formatter={(v: unknown) => [`${Number(v).toFixed(1)}%`]}
            labelFormatter={(label) => label.slice(0, 10)}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="strategy"
            stroke={color}
            strokeWidth={2}
            dot={false}
            name="AEGIS V3"
          />
          <Line
            type="monotone"
            dataKey="buyhold"
            stroke="#555"
            strokeWidth={1}
            dot={false}
            name="Buy & Hold"
            strokeDasharray="4 4"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

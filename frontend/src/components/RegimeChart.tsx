"use client";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import type { RegimePoint } from "@/lib/api";

const COLORS: Record<string, string> = {
  SPY: "#22c55e",
  QQQ: "#3b82f6",
  IWM: "#a855f7",
  BTC: "#f59e0b",
};

interface RegimeChartProps {
  data: RegimePoint[];
  asset: string;
}

export default function RegimeChart({ data, asset }: RegimeChartProps) {
  const color = COLORS[asset.toUpperCase()] || "#22c55e";
  const sampled = data.filter((_, i) => i % 5 === 0 || i === data.length - 1);

  const chartData = sampled.map((d) => ({
    ...d,
    crisis: d.regime === 0 ? d.exposure : 0,
    normal: d.regime === 1 ? d.exposure : 0,
  }));

  return (
    <div className="rounded-xl border p-5" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <h3 className="font-semibold mb-4">Exposure & Regime</h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#252525" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#737373", fontSize: 11 }}
            tickFormatter={(v) => v.slice(0, 7)}
            interval={Math.floor(sampled.length / 6)}
          />
          <YAxis tick={{ fill: "#737373", fontSize: 11 }} tickFormatter={(v) => `${v}%`} domain={[0, 100]} />
          <Tooltip
            contentStyle={{ background: "#1a1a1a", border: "1px solid #333", borderRadius: 8 }}
            labelStyle={{ color: "#999" }}
            formatter={(v: unknown) => [`${Number(v).toFixed(1)}%`]}
            labelFormatter={(label) => label.slice(0, 10)}
          />
          <Area
            type="stepAfter"
            dataKey="normal"
            fill={color}
            fillOpacity={0.3}
            stroke={color}
            strokeWidth={1}
            name="Normal"
          />
          <Area
            type="stepAfter"
            dataKey="crisis"
            fill="#ef4444"
            fillOpacity={0.3}
            stroke="#ef4444"
            strokeWidth={1}
            name="Crisis"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

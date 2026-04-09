"use client";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid,
} from "recharts";

interface PortfolioChartProps {
  data: { date: string; portfolio: number }[];
}

export default function PortfolioChart({ data }: PortfolioChartProps) {
  const sampled = data.filter((_, i) => i % 5 === 0 || i === data.length - 1);

  return (
    <div className="rounded-xl border p-5" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <h3 className="font-semibold mb-4">Portfolio Equity Curve (Equal Weight)</h3>
      <ResponsiveContainer width="100%" height={300}>
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
          <Line
            type="monotone"
            dataKey="portfolio"
            stroke="#22c55e"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

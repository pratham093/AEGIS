import type { Metrics } from "@/lib/api";
import StatCard from "./StatCard";

interface MetricsPanelProps {
  metrics: Metrics;
}

export default function MetricsPanel({ metrics }: MetricsPanelProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      <StatCard
        label="Sharpe Ratio"
        value={`${metrics.sized_sharpe > 0 ? "+" : ""}${metrics.sized_sharpe}`}
        subtext={`B&H: ${metrics.bh_sharpe}`}
        color={metrics.sized_sharpe > 0 ? "text-green-400" : "text-red-400"}
      />
      <StatCard
        label="Return"
        value={`${metrics.cum_return_sized_pct > 0 ? "+" : ""}${metrics.cum_return_sized_pct}%`}
        subtext={`B&H: ${metrics.cum_return_bh_pct}%`}
        color={metrics.cum_return_sized_pct >= 0 ? "text-green-400" : "text-red-400"}
      />
      <StatCard
        label="Max Drawdown"
        value={`${metrics.max_dd_sized_pct}%`}
        subtext={`B&H: ${metrics.max_dd_bh_pct}%`}
        color="text-red-400"
      />
      <StatCard
        label="Avg Exposure"
        value={`${metrics.avg_exposure_pct}%`}
      />
      <StatCard
        label="Win Rate"
        value={`${metrics.win_rate_pct}%`}
      />
      <StatCard
        label="VaR (95%)"
        value={`${metrics.avg_var95_pct}%`}
        subtext={`Vol: ${metrics.annualized_vol_pct}%`}
      />
    </div>
  );
}

"use client";
import { useState } from "react";

interface StepProps {
  title: string;
  color: string;
  items: string[];
  detail: string;
  expanded: boolean;
  onClick: () => void;
}

function Step({ title, color, items, detail, expanded, onClick }: StepProps) {
  return (
    <div
      onClick={onClick}
      className="rounded-xl border p-5 cursor-pointer transition-all duration-300"
      style={{
        borderColor: expanded ? color : "var(--card-border)",
        background: "var(--card)",
        boxShadow: expanded ? `0 0 20px ${color}20` : "none",
      }}
    >
      <div className="flex items-center gap-3 mb-3">
        <div
          className="w-3 h-3 rounded-full shrink-0"
          style={{ background: color }}
        />
        <h3 className="font-bold text-sm">{title}</h3>
      </div>
      <div className="space-y-1.5">
        {items.map((item) => (
          <div key={item} className="flex items-center gap-2 text-xs" style={{ color: "var(--muted)" }}>
            <span style={{ color }}>→</span>
            {item}
          </div>
        ))}
      </div>
      {expanded && (
        <p className="text-xs mt-3 pt-3 border-t leading-relaxed" style={{ borderColor: "var(--card-border)", color: "var(--muted)" }}>
          {detail}
        </p>
      )}
    </div>
  );
}

function Arrow({ color = "#22c55e" }: { color?: string }) {
  return (
    <div className="flex justify-center py-2">
      <svg width="24" height="32" viewBox="0 0 24 32" fill="none">
        <path d="M12 0 L12 24" stroke={color} strokeWidth="2" strokeDasharray="4 3" />
        <path d="M6 18 L12 26 L18 18" stroke={color} strokeWidth="2" fill="none" />
      </svg>
    </div>
  );
}

function HorizontalArrow({ color = "#22c55e" }: { color?: string }) {
  return (
    <div className="flex items-center justify-center">
      <svg width="40" height="24" viewBox="0 0 40 24" fill="none">
        <path d="M0 12 L32 12" stroke={color} strokeWidth="2" strokeDasharray="4 3" />
        <path d="M26 6 L34 12 L26 18" stroke={color} strokeWidth="2" fill="none" />
      </svg>
    </div>
  );
}

const STEPS = [
  {
    title: "DATA INGESTION",
    color: "#3b82f6",
    items: [
      "Yahoo Finance: SPY, QQQ, IWM, BTC, VIX, GLD, sectors",
      "FRED: Fed funds, treasury yields, CPI, unemployment",
      "Fama-French: Market, SMB, HML factor returns",
    ],
    detail: "Every day after market close, we pull the latest OHLCV prices from Yahoo Finance for all tracked instruments, plus macro indicators from FRED. Everything merges into a single unified dataset starting from 2014.",
  },
  {
    title: "FEATURE ENGINEERING",
    color: "#a855f7",
    items: [
      "49 features per asset computed from raw prices",
      "Returns, volatility, trend, momentum, volume",
      "Cross-asset: credit spread, VIX ratio, yield curve",
    ],
    detail: "Raw prices are transformed into 49 trading features: multi-horizon log returns, rolling volatility (5d to 63d), SMA distances, RSI, ATR, Bollinger position, sector dispersion, credit spreads, and more. All features are strictly causal — no future data leakage.",
  },
  {
    title: "REGIME DETECTION",
    color: "#f59e0b",
    items: [
      "GMM/HMM classifies market as NORMAL or CRISIS",
      "Inputs: volatility, returns, RSI, trend",
      "Trained on 10+ years of market history",
    ],
    detail: "A Gaussian Mixture Model (SPY/QQQ) or Hidden Markov Model (IWM/BTC) analyzes volatility, returns, momentum, and trend data to classify the current market state. CRISIS means elevated risk — the system automatically reduces exposure.",
  },
];

const SIGNAL_STEP = {
  title: "BASE RULE SIGNAL",
  color: "#22c55e",
  items: [
    "Check 1: Price above 50-day moving average",
    "Check 2: RSI above 40 (momentum not collapsing)",
    "Check 3: Volatility below 75th percentile",
  ],
  detail: "All three conditions must pass simultaneously. If any one fails, the signal is FLAT (stay in cash). This simple rule outperformed complex ML models in walk-forward testing because it can't invert during crashes.",
};

const RISK_LAYERS = [
  { name: "Portfolio Weight", desc: "SPY 30% / QQQ 25% / IWM 25% / BTC 20%", color: "#22c55e" },
  { name: "Vol Targeting", desc: "Scale to 15% annual vol (BTC: 40%)", color: "#3b82f6" },
  { name: "Regime Cap", desc: "Crisis → 50% max (BTC: 30%)", color: "#f59e0b" },
  { name: "VaR Limit", desc: "95th percentile daily loss cap", color: "#a855f7" },
  { name: "Drawdown Guard", desc: "-5% → 75%, -10% → 50%, -15% → 25%", color: "#ef4444" },
];

export default function Flowchart() {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <div className="space-y-1">
      {/* Data Pipeline */}
      <div className="grid md:grid-cols-3 gap-3">
        {STEPS.map((step, i) => (
          <Step
            key={step.title}
            {...step}
            expanded={expanded === i}
            onClick={() => setExpanded(expanded === i ? null : i)}
          />
        ))}
      </div>

      <Arrow color="#a855f7" />

      {/* Signal Check */}
      <Step
        {...SIGNAL_STEP}
        expanded={expanded === 3}
        onClick={() => setExpanded(expanded === 3 ? null : 3)}
      />

      <Arrow color="#22c55e" />

      {/* Risk Engine */}
      <div
        className="rounded-xl border p-5"
        style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="w-3 h-3 rounded-full bg-[#ef4444] shrink-0" />
          <h3 className="font-bold text-sm">RISK ENGINE (5 layers, applied sequentially)</h3>
        </div>
        <div className="flex flex-col md:flex-row items-stretch gap-2">
          {RISK_LAYERS.map((layer, i) => (
            <div key={layer.name} className="flex items-center gap-2 flex-1">
              <div
                className="rounded-lg p-3 flex-1 text-center border transition-all hover:scale-105"
                style={{ borderColor: `${layer.color}40`, background: `${layer.color}10` }}
              >
                <p className="text-xs font-semibold mb-1" style={{ color: layer.color }}>
                  {layer.name}
                </p>
                <p className="text-[10px] leading-tight" style={{ color: "var(--muted)" }}>
                  {layer.desc}
                </p>
              </div>
              {i < RISK_LAYERS.length - 1 && (
                <div className="hidden md:block">
                  <HorizontalArrow color={RISK_LAYERS[i + 1].color} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <Arrow color="#ef4444" />

      {/* Output */}
      <div className="grid md:grid-cols-2 gap-3">
        <div
          className="rounded-xl border p-5"
          style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-[#22c55e] shrink-0" />
            <h3 className="font-bold text-sm">IF ALL PASS + NORMAL REGIME</h3>
          </div>
          <div className="rounded-lg p-4 text-center bg-green-950/40 border border-green-800/30">
            <p className="text-xl font-bold text-[#22c55e]">GO LONG</p>
            <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
              Allocate risk-adjusted % of portfolio
            </p>
          </div>
        </div>
        <div
          className="rounded-xl border p-5"
          style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-[#ef4444] shrink-0" />
            <h3 className="font-bold text-sm">IF ANY FAIL OR CRISIS REGIME</h3>
          </div>
          <div className="rounded-lg p-4 text-center bg-neutral-900/40 border border-neutral-700/30">
            <p className="text-xl font-bold text-neutral-500">STAY FLAT</p>
            <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>
              0% exposure — capital protected in cash
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

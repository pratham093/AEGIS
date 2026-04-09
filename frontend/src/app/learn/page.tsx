import Link from "next/link";
import Navbar from "@/components/Navbar";
import Flowchart from "@/components/Flowchart";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border p-6 md:p-8" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <h2 className="text-xl font-bold mb-4">{title}</h2>
      {children}
    </div>
  );
}

function Term({ name, tldr, detail, example }: { name: string; tldr: string; detail: string; example?: string }) {
  return (
    <div className="py-4 border-b last:border-b-0" style={{ borderColor: "var(--card-border)" }}>
      <h3 className="font-semibold text-lg mb-1">{name}</h3>
      <p className="text-sm font-medium text-[#22c55e] mb-2">{tldr}</p>
      <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>{detail}</p>
      {example && (
        <p className="text-xs mt-2 italic" style={{ color: "var(--muted)" }}>Example: {example}</p>
      )}
    </div>
  );
}

export default function LearnPage() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)", color: "var(--foreground)" }}>
      <Navbar />

      <main className="max-w-3xl mx-auto px-8 py-12 space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Before You Invest</h1>
          <p style={{ color: "var(--muted)" }}>
            Everything you need to understand to read AEGIS signals and make informed decisions.
          </p>
        </div>

        {/* System Flowchart */}
        <Section title="How the System Works">
          <p className="text-sm mb-4" style={{ color: "var(--muted)" }}>
            From raw market data to the signal you see on the dashboard — click any step to learn more.
          </p>
          <Flowchart />
        </Section>

        {/* What the signals page shows */}
        <Section title="Reading the Signals Page">
          <Term
            name="Signal: GO LONG vs STAY FLAT"
            tldr="Should I buy or not?"
            detail="GO LONG means all entry conditions are met — the market is trending up, momentum is healthy, and volatility is manageable. The system is saying it's a good time to hold this asset. STAY FLAT means one or more conditions failed — sit in cash and wait."
          />
          <Term
            name="Allocation %"
            tldr="How much of your portfolio to put in"
            detail="When the signal is GO LONG, the allocation tells you what percentage of your capital to invest in that asset. 100% means full conviction. 50% means the system sees some risk and is being cautious. 0% means stay out entirely."
            example="If you have $10,000 and SPY shows GO LONG @ 60%, invest $6,000 in SPY."
          />
          <Term
            name="Market Regime"
            tldr="Is the market calm or panicking?"
            detail="AEGIS uses a statistical model (Gaussian Mixture Model) trained on 10+ years of data to classify the current market environment. NORMAL means typical conditions — trends work, entries are safe. CRISIS means elevated volatility and correlation spikes — the system protects capital by going flat."
          />
          <Term
            name="Risk Score (0-100)"
            tldr="How dangerous is the market right now?"
            detail="Combines volatility level, regime confidence, signal strength, and recent drawdown into a single number. 0-30 = low risk (green light). 30-60 = moderate (proceed with caution). 60-100 = high risk (the system is likely reducing or eliminating exposure)."
          />
        </Section>

        {/* Key metrics */}
        <Section title="Key Metrics Explained">
          <Term
            name="RSI (Relative Strength Index)"
            tldr="Is the price too high or too low?"
            detail="RSI measures how fast prices are rising vs falling over the last 14 days. Scale is 0-100. Above 70 = overbought (may pull back). Below 30 = oversold (may bounce). AEGIS requires RSI above 40 to enter — we don't buy into falling momentum."
            example="RSI 55 = healthy momentum. RSI 25 = severe selling, stay away. RSI 80 = might be overextended."
          />
          <Term
            name="Volatility (Annualized %)"
            tldr="How wild are the price swings?"
            detail="Measured as the annualized standard deviation of daily returns over 21 days. SPY normally sits at 12-16%. Above 25% = turbulent. Above 35% = crisis territory. AEGIS won't enter if volatility is above the 75th percentile of the past year."
            example="Volatility 14% = calm market. Volatility 30% = storm (March 2020, April 2025 tariffs)."
          />
          <Term
            name="VaR 95% (Value at Risk)"
            tldr="What's the worst daily loss you should expect?"
            detail="The 5th percentile of historical daily returns. If VaR is -1.5%, that means on 95% of days, you won't lose more than 1.5% of your position. Worse losses can happen on the other 5% of days."
            example="VaR -1.2% on a $10,000 position = expect to lose at most $120 on a bad day."
          />
          <Term
            name="SMA-50 (50-Day Moving Average)"
            tldr="Is the overall trend up or down?"
            detail="The average closing price over the last 50 trading days. If the current price is ABOVE the SMA-50, the trend is up. If below, the trend is down. AEGIS only buys when price is above SMA-50 — we follow the trend, not fight it."
          />
          <Term
            name="Sharpe Ratio"
            tldr="Return per unit of risk taken"
            detail="Measures how much return you get for each unit of volatility. Above 1.0 = good. Above 2.0 = excellent. Below 0 = losing money. AEGIS's backtest portfolio Sharpe is 2.63 — meaning strong returns with controlled risk."
            example="Sharpe 0.5 = meh. Sharpe 1.5 = solid. Sharpe 2.5 = exceptional."
          />
          <Term
            name="Max Drawdown"
            tldr="The worst peak-to-trough loss"
            detail="The largest drop from a high point to a low point during the entire period. A max drawdown of -5.6% means at worst, your portfolio dropped 5.6% from its peak before recovering. Compare to the S&P 500 which drew down -41% over the same period."
          />
        </Section>

        {/* The 4 assets */}
        <Section title="The Assets We Track">
          <Term
            name="SPY — S&P 500 ETF"
            tldr="The US stock market"
            detail="Tracks the 500 largest US companies. The benchmark for 'the market.' If you're only going to invest in one thing, this is it. Diversified across all sectors."
          />
          <Term
            name="QQQ — Nasdaq 100 ETF"
            tldr="Big tech stocks"
            detail="Tracks the 100 largest non-financial companies on the Nasdaq. Heavy in tech: Apple, Microsoft, Google, Amazon, Nvidia. Higher growth potential but also more volatile than SPY."
          />
          <Term
            name="IWM — Russell 2000 ETF"
            tldr="Small-cap US stocks"
            detail="Tracks 2,000 small US companies. More volatile and more sensitive to the economy than SPY. Tends to lead in recoveries but fall harder in downturns."
          />
          <Term
            name="BTC — Bitcoin"
            tldr="Digital asset / crypto"
            detail="The largest cryptocurrency by market cap. Trades 24/7 unlike stocks. Much more volatile — daily swings of 3-5% are normal. AEGIS uses tighter risk controls for BTC: lower crisis caps and no position smoothing."
          />
        </Section>

        {/* Risk flags */}
        <Section title="Risk Flags — What They Mean">
          <Term
            name="CRISIS REGIME"
            tldr="The market is in a dangerous state"
            detail="The regime model has detected conditions similar to past crashes (2020, 2022). Volatility is elevated, correlations are spiking. AEGIS caps exposure to 50% max (30% for BTC) during crisis."
          />
          <Term
            name="LOW CONFIDENCE"
            tldr="The signal isn't strong enough"
            detail="The ranking of the current signal probability is below the 30th percentile of recent readings. Not enough edge to justify entry."
          />
          <Term
            name="DRAWDOWN GUARD"
            tldr="Recent losses triggered protection"
            detail="The portfolio has dropped more than 5% from its recent peak. AEGIS automatically scales down exposure to limit further damage. Below -10%, exposure is halved."
          />
          <Term
            name="HIGH VOL"
            tldr="Volatility is way above normal"
            detail="Current realized volatility exceeds 2x the target level. Position sizes are automatically reduced through volatility targeting."
          />
        </Section>

        {/* How AEGIS decides */}
        <Section title="How AEGIS Makes Decisions">
          <div className="text-sm leading-relaxed space-y-4" style={{ color: "var(--muted)" }}>
            <p>
              <strong style={{ color: "var(--foreground)" }}>Step 1: Entry check.</strong>{" "}
              Three conditions must ALL pass: price above 50-day moving average (trend is up),
              RSI above 40 (momentum isn&apos;t collapsing), and volatility below the 75th percentile
              of the past year (not too wild). If any one fails, the signal is FLAT.
            </p>
            <p>
              <strong style={{ color: "var(--foreground)" }}>Step 2: Regime detection.</strong>{" "}
              A Gaussian Mixture Model trained on volatility, returns, RSI, and trend data classifies
              the market as NORMAL or CRISIS. In crisis, maximum exposure is capped at 50%.
            </p>
            <p>
              <strong style={{ color: "var(--foreground)" }}>Step 3: Position sizing.</strong>{" "}
              The risk engine sets allocation using volatility targeting (aim for 15% annual vol),
              regime caps, VaR limits, and drawdown guards. The result is a specific allocation %
              that balances opportunity with protection.
            </p>
            <p>
              <strong style={{ color: "var(--foreground)" }}>Step 4: Smoothing.</strong>{" "}
              For SPY and QQQ, an exponential moving average smooths daily exposure changes to avoid
              whipsawing in and out. IWM and BTC use no smoothing for faster exits during crashes.
            </p>
          </div>
        </Section>

        <div className="text-center pt-4">
          <Link href="/signals" className="inline-block px-8 py-3 rounded-lg bg-[#22c55e] text-black font-semibold hover:bg-[#16a34a] transition-colors">
            View Today&apos;s Signals
          </Link>
        </div>
      </main>

      <footer className="border-t px-8 py-6 text-center text-xs" style={{ borderColor: "var(--card-border)", color: "var(--muted)" }}>
        AEGIS V3 — Educational content only. Not financial advice.
      </footer>
    </div>
  );
}

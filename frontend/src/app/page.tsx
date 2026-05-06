import Navbar from "@/components/Navbar";
import VantaBackground from "@/components/VantaBackground";
import CursorGlow from "@/components/CursorGlow";
import HeroSection from "@/components/HeroSection";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col relative" style={{ background: "var(--background)", color: "var(--foreground)" }}>
      <VantaBackground />
      <CursorGlow />
      <div className="relative z-10 flex flex-col min-h-screen">
        <Navbar />

        <div className="px-8 pt-4">
          <div className="max-w-4xl mx-auto rounded-lg border px-4 py-2.5 flex items-center justify-center gap-2 text-xs" style={{ borderColor: "var(--card-border)", background: "var(--card)", color: "var(--muted)" }}>
            <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-pulse" />
            Heads up: the backend runs on a free tier and may take 30–50 seconds to wake up on first load. Refreshing signals can take a moment too.
          </div>
        </div>

        <HeroSection />

        <section className="px-8 py-16 border-t" style={{ borderColor: "var(--card-border)" }}>
          <div className="max-w-4xl mx-auto">
            <p className="text-center text-xs uppercase tracking-widest mb-8" style={{ color: "var(--muted)" }}>
              Walk-forward backtest results (2015 — 2026)
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { value: "2.63", label: "Portfolio Sharpe", color: "#22c55e" },
                { value: "-5.6%", label: "Max Drawdown", color: "#ef4444" },
                { value: "+232%", label: "Total Return", color: "#22c55e" },
                { value: "10+ years", label: "Backtested", color: "#3b82f6" },
              ].map((s) => (
                <div key={s.label} className="text-center">
                  <p className="text-3xl font-bold mb-1" style={{ color: s.color }}>{s.value}</p>
                  <p className="text-xs" style={{ color: "var(--muted)" }}>{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <footer className="border-t px-8 py-6 text-center text-xs" style={{ borderColor: "var(--card-border)", color: "var(--muted)" }}>
          AEGIS V3 — Not financial advice. Past performance does not guarantee future results.
        </footer>
      </div>
    </div>
  );
}

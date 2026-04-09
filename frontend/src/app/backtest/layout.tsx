import Link from "next/link";
import ThemeToggle from "@/components/ThemeToggle";

const NAV_ITEMS = [
  { href: "/", label: "Live Signals" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/backtest", label: "Backtest Results" },
  { href: "/backtest/asset/spy", label: "SPY", color: "#22c55e" },
  { href: "/backtest/asset/qqq", label: "QQQ", color: "#3b82f6" },
  { href: "/backtest/asset/iwm", label: "IWM", color: "#a855f7" },
  { href: "/backtest/asset/btc", label: "BTC", color: "#f59e0b" },
];

export default function BacktestLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">
      <nav className="w-56 border-r p-5 flex flex-col gap-1 shrink-0"
        style={{ borderColor: "var(--card-border)", background: "var(--nav-bg)" }}>
        <Link href="/" className="flex items-center gap-2 mb-2">
          <img src="/dark.png" alt="" className="h-6 dark-logo" />
          <img src="/light.png" alt="" className="h-6 light-logo" />
          <span className="text-xl font-bold tracking-tight">AEGIS</span>
        </Link>
        <div className="mb-4">
          <ThemeToggle />
        </div>
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2"
            style={{ color: "var(--foreground)" }}
          >
            {item.color && (
              <span className="w-2 h-2 rounded-full" style={{ background: item.color }} />
            )}
            {item.label}
          </Link>
        ))}
      </nav>
      <main className="flex-1 p-8 overflow-auto">
        {children}
      </main>
    </div>
  );
}

"use client";
import { useEffect, useRef } from "react";
import Link from "next/link";

export default function HeroSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const onMouse = (e: MouseEvent) => {
      const rect = section.getBoundingClientRect();
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };

      section.style.setProperty("--mx", `${e.clientX}px`);
      section.style.setProperty("--my", `${e.clientY}px`);

      const elements = section.querySelectorAll("[data-glow]");
      elements.forEach((el) => {
        const elRect = el.getBoundingClientRect();
        const elCenterX = elRect.left + elRect.width / 2;
        const elCenterY = elRect.top + elRect.height / 2;
        const dx = e.clientX - elCenterX;
        const dy = e.clientY - elCenterY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = 400;
        const proximity = Math.max(0, 1 - dist / maxDist);

        const htmlEl = el as HTMLElement;
        htmlEl.style.textShadow = proximity > 0.05
          ? `0 0 ${proximity * 40}px rgba(34, 197, 94, ${proximity * 0.6}), 0 0 ${proximity * 80}px rgba(34, 197, 94, ${proximity * 0.2})`
          : "none";
      });

      const cards = section.querySelectorAll("[data-card]");
      cards.forEach((card) => {
        const cardRect = card.getBoundingClientRect();
        const cardCenterX = cardRect.left + cardRect.width / 2;
        const cardCenterY = cardRect.top + cardRect.height / 2;
        const dx2 = e.clientX - cardCenterX;
        const dy2 = e.clientY - cardCenterY;
        const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
        const proximity2 = Math.max(0, 1 - dist2 / 350);

        const htmlCard = card as HTMLElement;
        htmlCard.style.borderColor = proximity2 > 0.1
          ? `rgba(34, 197, 94, ${proximity2 * 0.5})`
          : "var(--card-border)";
        htmlCard.style.boxShadow = proximity2 > 0.1
          ? `0 0 ${proximity2 * 25}px rgba(34, 197, 94, ${proximity2 * 0.1})`
          : "none";
      });
    };

    window.addEventListener("mousemove", onMouse);
    return () => window.removeEventListener("mousemove", onMouse);
  }, []);

  return (
    <section
      ref={sectionRef}
      className="flex-1 flex flex-col items-center justify-center text-center px-8 py-28 max-w-4xl mx-auto"
    >
      <div className="mb-6 inline-flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-full border" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
        <span className="w-2 h-2 rounded-full bg-[#22c55e] animate-pulse" />
        Signals updated daily after market close
      </div>

      <h1 className="text-5xl md:text-7xl font-bold tracking-tight leading-[1.1] mb-6 transition-all duration-150">
        <span data-glow className="inline-block transition-all duration-150">
          Know When to
        </span>
        <br />
        <span data-glow className="text-[#22c55e] inline-block transition-all duration-150">
          Enter and Exit
        </span>
      </h1>

      <p data-glow className="text-lg md:text-xl max-w-2xl mb-12 leading-relaxed transition-all duration-150" style={{ color: "var(--foreground)", opacity: 0.85 }}>
        AEGIS analyzes market regime, trend, momentum, and volatility across
        SPY, QQQ, IWM, and BTC — then tells you exactly what to do.
        No guessing. No emotions.
      </p>

      <div className="flex gap-4 mb-20">
        <Link href="/signals" className="px-8 py-3.5 rounded-lg bg-[#22c55e] text-black font-semibold hover:bg-[#16a34a] transition-colors text-lg">
          View Today&apos;s Signals
        </Link>
        <Link href="/learn" className="px-8 py-3.5 rounded-lg border font-semibold transition-colors text-lg hover:border-[#22c55e] hover:text-[#22c55e]" style={{ borderColor: "var(--card-border)" }}>
          How It Works
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-8 w-full max-w-4xl text-left">
        <div data-card className="rounded-xl border p-6 transition-all duration-200" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
          <div className="w-10 h-10 rounded-lg bg-[#22c55e]/10 flex items-center justify-center mb-4">
            <span className="text-[#22c55e] text-lg font-bold">1</span>
          </div>
          <h3 className="font-semibold mb-2">We Read the Market</h3>
          <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>
            Every day after market close, AEGIS pulls live data and checks if the market
            is trending up, where RSI sits, and how volatile things are.
          </p>
        </div>
        <div data-card className="rounded-xl border p-6 transition-all duration-200" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
          <div className="w-10 h-10 rounded-lg bg-[#3b82f6]/10 flex items-center justify-center mb-4">
            <span className="text-[#3b82f6] text-lg font-bold">2</span>
          </div>
          <h3 className="font-semibold mb-2">We Detect the Regime</h3>
          <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>
            Our regime model classifies the market as NORMAL or CRISIS.
            In crisis, we pull back. In normal conditions, we look for entries.
          </p>
        </div>
        <div data-card className="rounded-xl border p-6 transition-all duration-200" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
          <div className="w-10 h-10 rounded-lg bg-[#f59e0b]/10 flex items-center justify-center mb-4">
            <span className="text-[#f59e0b] text-lg font-bold">3</span>
          </div>
          <h3 className="font-semibold mb-2">You Get a Clear Signal</h3>
          <p className="text-sm leading-relaxed" style={{ color: "var(--muted)" }}>
            GO LONG with a specific allocation %, or STAY FLAT.
            No ambiguity. We also show you exactly why — every metric is transparent.
          </p>
        </div>
      </div>
    </section>
  );
}

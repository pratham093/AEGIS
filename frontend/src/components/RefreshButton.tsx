"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function RefreshButton() {
  const router = useRouter();
  const [spinning, setSpinning] = useState(false);
  const [error, setError] = useState("");

  const handleRefresh = async () => {
    setSpinning(true);
    setError("");
    try {
      const res = await fetch("/api/signals/refresh", { method: "POST" });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: "Refresh failed" }));
        setError(body.detail || "Refresh failed");
      } else {
        router.refresh();
      }
    } catch {
      setError("Could not reach backend");
    } finally {
      setSpinning(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleRefresh}
        disabled={spinning}
        className="flex items-center gap-2 text-sm px-4 py-2 rounded-lg border transition-colors hover:border-[#22c55e] hover:text-[#22c55e] disabled:opacity-50"
        style={{ borderColor: "var(--card-border)" }}
        title="Regenerate signals with latest market data"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className={spinning ? "animate-spin" : ""}
        >
          <path d="M21 2v6h-6" />
          <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
          <path d="M3 22v-6h6" />
          <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
        </svg>
        {spinning ? "Refreshing..." : "Refresh"}
      </button>
      {error && <span className="text-xs text-red-400">{error}</span>}
    </div>
  );
}

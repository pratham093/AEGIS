"use client";

import { useState } from "react";
import { fetchNewsShuffle } from "@/lib/api";
import type { NewsArticle } from "@/lib/api";

const COLORS: Record<string, string> = {
  SPY: "#22c55e", QQQ: "#3b82f6", IWM: "#a855f7", BTC: "#f59e0b",
};

export default function MarketNews({ initial }: { initial: NewsArticle[] }) {
  const [articles, setArticles] = useState(initial);
  const [loading, setLoading] = useState(false);

  const shuffle = async () => {
    setLoading(true);
    try {
      const data = await fetchNewsShuffle();
      setArticles(data.articles || []);
    } catch {
      // keep existing articles
    }
    setLoading(false);
  };

  if (articles.length === 0) return null;

  return (
    <div className="mt-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Market News</h2>
        <button
          onClick={shuffle}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors"
          style={{
            borderColor: "var(--card-border)",
            color: "var(--muted)",
            background: "var(--card)",
          }}
        >
          <svg
            className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Shuffle
        </button>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {articles.map((article) => (
          <a
            key={article.id}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-xl border p-4 flex gap-4 transition-colors group"
            style={{ borderColor: "var(--card-border)", background: "var(--card)" }}
          >
            {article.thumbnail && (
              <img
                src={article.thumbnail}
                alt=""
                className="w-24 h-24 rounded-lg object-cover shrink-0"
              />
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1.5">
                <span
                  className="text-xs font-semibold px-1.5 py-0.5 rounded"
                  style={{
                    background: `${COLORS[article.ticker] || "#666"}20`,
                    color: COLORS[article.ticker] || "#666",
                  }}
                >
                  {article.ticker}
                </span>
                <span className="text-xs" style={{ color: "var(--muted)" }}>
                  {article.publisher}
                </span>
              </div>
              <h3 className="font-semibold text-sm leading-snug mb-1 group-hover:text-[#22c55e] transition-colors line-clamp-2">
                {article.title}
              </h3>
              {article.summary && (
                <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "var(--muted)" }}>
                  {article.summary}
                </p>
              )}
              <p className="text-xs mt-1.5" style={{ color: "var(--muted)" }}>
                {new Date(article.date).toLocaleDateString("en-US", {
                  month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
                })}
              </p>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}

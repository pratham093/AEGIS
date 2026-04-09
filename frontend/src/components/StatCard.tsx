interface StatCardProps {
  label: string;
  value: string;
  subtext?: string;
  color?: string;
}

export default function StatCard({ label, value, subtext, color }: StatCardProps) {
  return (
    <div className="rounded-xl border p-5" style={{ borderColor: "var(--card-border)", background: "var(--card)" }}>
      <p className="text-sm mb-1" style={{ color: "var(--muted)" }}>{label}</p>
      <p className={`text-2xl font-bold ${color || ""}`}>{value}</p>
      {subtext && <p className="text-xs mt-1" style={{ color: "var(--muted)" }}>{subtext}</p>}
    </div>
  );
}

type StatusBadgeProps = {
  label: string;
  tone?: "default" | "accent";
};

export function StatusBadge({ label, tone = "default" }: StatusBadgeProps) {
  const toneClass =
    tone === "accent"
      ? "bg-amber-300 text-slate-950"
      : "bg-slate-950/5 text-slate-700";

  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] ${toneClass}`}>
      {label}
    </span>
  );
}

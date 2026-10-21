interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const norm = status.toUpperCase();

  let styles = "bg-slate-100 text-slate-700 border-slate-200";
  if (["COMPLETED", "ACTIVE", "HEALTHY", "BEST", "OPTIMAL"].includes(norm)) {
    styles = "bg-emerald-50 text-emerald-700 border-emerald-200";
  } else if (["RUNNING", "IN_PROGRESS", "PROCESSING"].includes(norm)) {
    styles = "bg-blue-50 text-blue-700 border-blue-200 animate-pulse";
  } else if (["QUEUED", "PENDING"].includes(norm)) {
    styles = "bg-amber-50 text-amber-700 border-amber-200";
  } else if (["FAILED", "ERROR", "STOCKOUT_RISK"].includes(norm)) {
    styles = "bg-rose-50 text-rose-700 border-rose-200";
  } else if (["EXCESS_STOCK"].includes(norm)) {
    styles = "bg-purple-50 text-purple-700 border-purple-200";
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${styles} ${className}`}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}


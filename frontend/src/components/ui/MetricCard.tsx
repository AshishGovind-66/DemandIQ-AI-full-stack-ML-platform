import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: string;
  trendPositive?: boolean;
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendPositive,
  className = "",
}: MetricCardProps) {
  return (
    <div
      className={`bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow transition-shadow ${className}`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-slate-900">{value}</div>
        {(subtitle || trend) && (
          <div className="mt-1 flex items-center space-x-2 text-xs">
            {trend && (
              <span
                className={`font-semibold ${
                  trendPositive ? "text-emerald-600" : "text-rose-600"
                }`}
              >
                {trend}
              </span>
            )}
            {subtitle && <span className="text-slate-500">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
}


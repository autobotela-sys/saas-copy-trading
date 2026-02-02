'use client';

interface SummaryCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  highlight?: boolean;
}

export function SummaryCard({ title, value, subtitle, trend, highlight }: SummaryCardProps) {
  const formattedValue = typeof value === 'number' 
    ? (value >= 0 ? `+$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : `-$${Math.abs(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`)
    : value;

  const valueColor = typeof value === 'number' 
    ? (value >= 0 ? 'text-emerald-500' : 'text-rose-500')
    : 'text-[#0d181c] dark:text-white';

  return (
    <div
      className={`bg-white dark:bg-background-dark p-6 rounded-xl border shadow-sm ${
        highlight
          ? 'border-2 border-primary/20 bg-primary/5'
          : 'border-[#cee2e8] dark:border-gray-800'
      }`}
    >
      <p className={`text-sm font-medium ${highlight ? 'text-primary font-bold' : 'text-[#49879c]'}`}>
        {title}
      </p>
      <h3 className={`text-2xl font-bold mt-1 ${highlight ? 'text-primary' : valueColor}`}>
        {formattedValue}
      </h3>
      {trend && (
        <div
          className={`flex items-center gap-1 mt-2 font-medium text-sm ${
            trend.isPositive ? 'text-emerald-500' : 'text-rose-500'
          }`}
        >
          <span className="material-symbols-outlined text-sm">
            {trend.isPositive ? 'trending_up' : 'trending_down'}
          </span>
          {trend.value}
        </div>
      )}
      {subtitle && (
        <div className="flex items-center gap-1 mt-2 text-[#49879c] font-medium text-sm">
          {subtitle}
        </div>
      )}
    </div>
  );
}

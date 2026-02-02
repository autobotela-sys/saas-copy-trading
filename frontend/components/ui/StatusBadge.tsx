'use client';

interface StatusBadgeProps {
  status: 'ACTIVE' | 'EXPIRED' | 'PENDING' | 'INACTIVE';
  size?: 'sm' | 'md' | 'lg';
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const statusConfig = {
    ACTIVE: {
      bg: 'bg-emerald-100 dark:bg-emerald-900/30',
      text: 'text-emerald-700 dark:text-emerald-400',
      label: 'Active',
    },
    EXPIRED: {
      bg: 'bg-rose-100 dark:bg-rose-900/30',
      text: 'text-rose-700 dark:text-rose-400',
      label: 'Expired',
    },
    PENDING: {
      bg: 'bg-yellow-100 dark:bg-yellow-900/30',
      text: 'text-yellow-700 dark:text-yellow-400',
      label: 'Pending',
    },
    INACTIVE: {
      bg: 'bg-gray-100 dark:bg-gray-800',
      text: 'text-gray-700 dark:text-gray-400',
      label: 'Inactive',
    },
  };

  const config = statusConfig[status];
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs',
    lg: 'px-3 py-1.5 text-sm',
  };

  return (
    <span className={`inline-flex items-center rounded-full font-bold ${config.bg} ${config.text} ${sizeClasses[size]}`}>
      {config.label}
    </span>
  );
}

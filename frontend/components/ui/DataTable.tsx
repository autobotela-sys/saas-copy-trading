'use client';

import { ReactNode } from 'react';

interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => ReactNode;
  align?: 'left' | 'right' | 'center';
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
}

export function DataTable<T extends { id?: number | string }>({
  columns,
  data,
  loading = false,
  emptyMessage = 'No data available',
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 overflow-hidden">
        <div className="p-8 text-center text-[#49879c]">Loading...</div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 overflow-hidden">
        <div className="p-8 text-center text-[#49879c]">{emptyMessage}</div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-800/50 text-[#49879c] text-xs uppercase font-bold tracking-wider">
              {columns.map((column) => (
                <th
                  key={String(column.key)}
                  className={`px-6 py-4 ${column.align === 'right' ? 'text-right' : column.align === 'center' ? 'text-center' : ''}`}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
            {data.map((item) => (
              <tr
                key={item.id || Math.random()}
                className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors"
              >
                {columns.map((column) => (
                  <td
                    key={String(column.key)}
                    className={`px-6 py-4 ${column.align === 'right' ? 'text-right' : column.align === 'center' ? 'text-center' : ''}`}
                  >
                    {column.render ? column.render(item) : String(item[column.key as keyof T] || '-')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

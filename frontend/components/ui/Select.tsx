'use client';

import { SelectHTMLAttributes, forwardRef } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: Array<{ value: string; label: string }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-2">
        {label && (
          <label className="text-[#0d181c] dark:text-white text-sm font-semibold leading-normal">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={`form-select bg-white dark:bg-background-dark border rounded-lg text-sm focus:ring-primary focus:border-primary py-2 px-4 min-w-[120px] text-[#0d181c] dark:text-white ${
            error ? 'border-rose-500' : 'border-[#cee2e8] dark:border-gray-800'
          } ${className}`}
          {...props}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {error && <p className="text-sm text-rose-500">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';

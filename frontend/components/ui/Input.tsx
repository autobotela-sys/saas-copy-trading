'use client';

import { InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-2">
        {label && (
          <label className="text-[#0d181c] dark:text-white text-sm font-semibold leading-normal">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={`form-input flex w-full min-w-0 resize-none overflow-hidden rounded-lg text-[#0d181c] dark:text-white focus:outline-0 focus:ring-2 focus:ring-primary/50 border bg-white dark:bg-slate-800/50 h-14 placeholder:text-[#49879c] dark:placeholder:text-slate-500 p-[15px] text-base font-normal leading-normal transition-all ${
            error ? 'border-rose-500' : 'border-[#cee2e8] dark:border-slate-700'
          } ${className}`}
          {...props}
        />
        {error && <p className="text-sm text-rose-500">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

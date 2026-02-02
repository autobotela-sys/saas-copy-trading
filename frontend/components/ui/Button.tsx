'use client';

import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  icon?: string;
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  icon,
  className = '',
  ...props
}: ButtonProps) {
  const baseClasses = 'font-bold rounded-lg transition-colors flex items-center justify-center gap-2';
  
  const variantClasses = {
    primary: 'bg-primary text-white hover:opacity-90',
    secondary: 'bg-white dark:bg-background-dark border border-[#cee2e8] dark:border-gray-800 text-[#0d181c] dark:text-white hover:bg-gray-50 dark:hover:bg-gray-800',
    danger: 'bg-rose-50 text-rose-600 border border-rose-200 hover:bg-rose-100',
    ghost: 'bg-transparent text-[#49879c] hover:bg-gray-100 dark:hover:bg-gray-800',
  };

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {icon && <span className="material-symbols-outlined text-sm">{icon}</span>}
      {children}
    </button>
  );
}

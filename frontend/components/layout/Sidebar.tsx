'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { logout } from '@/lib/auth';

interface NavItem {
  href: string;
  icon: string;
  label: string;
}

const userNavItems: NavItem[] = [
  { href: '/dashboard', icon: 'dashboard', label: 'Dashboard' },
  { href: '/profile', icon: 'person', label: 'Profile' },
  { href: '/profile/broker', icon: 'account_balance_wallet', label: 'Brokers' },
  { href: '/profile/trading', icon: 'settings', label: 'Trading Settings' },
  { href: '/notifications', icon: 'notifications', label: 'Notifications' },
  { href: '/support', icon: 'support_agent', label: 'Support' },
];

const adminNavItems: NavItem[] = [
  { href: '/admin/dashboard', icon: 'dashboard', label: 'Dashboard' },
  { href: '/admin/users', icon: 'group', label: 'Users' },
  { href: '/profile/broker', icon: 'settings_input_component', label: 'Broker Settings' },
  { href: '/admin/history', icon: 'receipt_long', label: 'Trade Logs' },
  { href: '/admin/health', icon: 'analytics', label: 'System Health' },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const isAdmin = user?.role === 'ADMIN';
  const navItems = isAdmin ? adminNavItems : userNavItems;

  return (
    <aside className="w-64 border-r border-[#cee2e8] dark:border-gray-800 bg-white dark:bg-background-dark flex flex-col shrink-0">
      <div className="p-6 flex items-center gap-3">
        <div className="bg-primary flex items-center justify-center rounded-lg size-10 text-white">
          <span className="material-symbols-outlined">bolt</span>
        </div>
        <div className="flex flex-col">
          <h1 className="text-[#0d181c] dark:text-white text-base font-bold leading-none">Zap Copy</h1>
          <p className="text-[#49879c] text-xs font-normal">Multi-Broker SaaS</p>
        </div>
      </div>
      <nav className="flex-1 px-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-[#49879c] hover:bg-gray-100 dark:hover:bg-gray-800'
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <p className="text-sm font-medium">{item.label}</p>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-[#cee2e8] dark:border-gray-800">
        <div className="flex items-center gap-3">
          <div className="size-10 rounded-full bg-primary/20 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary">person</span>
          </div>
          <div className="flex flex-col flex-1 min-w-0">
            <p className="text-sm font-bold truncate">{user?.email || 'User'}</p>
            <p className="text-xs text-[#49879c]">{user?.role || 'USER'}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="mt-2 w-full text-left px-3 py-2 text-sm text-[#49879c] hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        >
          <span className="material-symbols-outlined text-sm align-middle mr-2">logout</span>
          Logout
        </button>
      </div>
    </aside>
  );
}

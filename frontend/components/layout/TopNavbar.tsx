'use client';

interface TopNavbarProps {
  title: string;
  showSearch?: boolean;
  searchPlaceholder?: string;
  actions?: React.ReactNode;
}

export function TopNavbar({ title, showSearch = false, searchPlaceholder = 'Search...', actions }: TopNavbarProps) {
  return (
    <header className="h-16 border-b border-[#cee2e8] dark:border-gray-800 bg-white dark:bg-background-dark px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-6">
        <h2 className="text-lg font-bold text-[#0d181c] dark:text-white">{title}</h2>
        {showSearch && (
          <div className="relative w-64">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#49879c] text-xl">
              search
            </span>
            <input
              className="w-full bg-gray-100 dark:bg-gray-800 border-none rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-primary/50 text-[#0d181c] dark:text-white placeholder:text-[#49879c] dark:placeholder:text-slate-500"
              placeholder={searchPlaceholder}
              type="text"
            />
          </div>
        )}
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-[#49879c] hover:text-primary transition-colors">
          <span className="material-symbols-outlined">notifications</span>
        </button>
        {actions}
      </div>
    </header>
  );
}

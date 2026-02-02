'use client';

import { useQuery } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { SummaryCard } from '@/components/ui/SummaryCard';
import { Button } from '@/components/ui/Button';
import { userApi, Position } from '@/lib/api';
import { useRequireAuth } from '@/hooks/useAuth';
import { format } from 'date-fns';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, loading } = useRequireAuth();

  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => userApi.getDashboard(),
    refetchInterval: 10000, // Refresh every 10 seconds
    enabled: !loading,
  });

  const { data: positions, isLoading: positionsLoading } = useQuery({
    queryKey: ['positions', 'OPEN'],
    queryFn: () => userApi.getPositions('OPEN'),
    refetchInterval: 10000,
    enabled: !loading,
  });

  if (loading || dashboardLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const tokenTimeRemaining = dashboard?.token_status?.time_remaining || '00:00:00';

  return (
    <Layout>
      <TopNavbar title="User Dashboard" showSearch searchPlaceholder="Search markets..." />
      <div className="p-8 space-y-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <SummaryCard
            title="Total P&L"
            value={dashboard?.total_pnl || 0}
            trend={
              dashboard?.total_pnl
                ? {
                    value: `${((dashboard.total_pnl / 100000) * 100).toFixed(1)}%`,
                    isPositive: dashboard.total_pnl >= 0,
                  }
                : undefined
            }
          />
          <SummaryCard
            title="Today's P&L"
            value={dashboard?.today_pnl || 0}
            trend={
              dashboard?.today_pnl
                ? {
                    value: `${((dashboard.today_pnl / 10000) * 100).toFixed(1)}%`,
                    isPositive: dashboard.today_pnl >= 0,
                  }
                : undefined
            }
          />
          <SummaryCard
            title="Open Positions"
            value={dashboard?.open_positions_count || 0}
            subtitle="Active Contracts"
          />
          <SummaryCard
            title="Broker Token Status"
            value={tokenTimeRemaining}
            subtitle="Time till refresh"
            highlight
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex gap-2">
            <Button variant="primary" size="sm">
              Open
            </Button>
            <Button variant="secondary" size="sm">
              Closed
            </Button>
            <Button variant="secondary" size="sm">
              All
            </Button>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Open Positions Table */}
          <div className="lg:col-span-2 bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 overflow-hidden">
            <div className="p-6 border-b border-[#cee2e8] dark:border-gray-800 flex justify-between items-center">
              <h4 className="font-bold text-lg">Open Positions</h4>
              <Button variant="ghost" size="sm" icon="refresh">
                Refresh
              </Button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 dark:bg-gray-800/50 text-[#49879c] text-xs uppercase font-bold tracking-wider">
                    <th className="px-6 py-4">Symbol</th>
                    <th className="px-4 py-4">Expiry</th>
                    <th className="px-4 py-4">Strike</th>
                    <th className="px-4 py-4">Type</th>
                    <th className="px-4 py-4">Qty</th>
                    <th className="px-4 py-4 text-right">LTP</th>
                    <th className="px-4 py-4 text-right">P&L</th>
                    <th className="px-6 py-4 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                  {positionsLoading ? (
                    <tr>
                      <td colSpan={8} className="px-6 py-8 text-center text-[#49879c]">
                        Loading positions...
                      </td>
                    </tr>
                  ) : positions && positions.length > 0 ? (
                    positions.map((position: Position) => (
                      <tr
                        key={position.id}
                        className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors"
                      >
                        <td className="px-6 py-4 font-bold">{position.symbol}</td>
                        <td className="px-4 py-4 text-sm">{format(new Date(position.expiry), 'dd-MMM')}</td>
                        <td className="px-4 py-4 text-sm">{position.strike}</td>
                        <td className="px-4 py-4">
                          <span
                            className={`px-2 py-1 rounded text-xs font-bold ${
                              position.option_type === 'CE'
                                ? 'bg-emerald-100 text-emerald-700'
                                : 'bg-rose-100 text-rose-700'
                            }`}
                          >
                            {position.option_type}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm">{position.quantity}</td>
                        <td className="px-4 py-4 text-right font-medium">
                          {position.current_price?.toFixed(2) || '-'}
                        </td>
                        <td
                          className={`px-4 py-4 text-right font-bold ${
                            position.pnl >= 0 ? 'text-emerald-500' : 'text-rose-500'
                          }`}
                        >
                          {position.pnl >= 0 ? '+' : ''}${position.pnl.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 text-center">
                          <Link href={`/positions/${position.id}/close`}>
                            <Button variant="danger" size="sm">
                              Close
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={8} className="px-6 py-8 text-center text-[#49879c]">
                        No open positions
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Trades List */}
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm flex flex-col">
            <div className="p-6 border-b border-[#cee2e8] dark:border-gray-800">
              <h4 className="font-bold text-lg">Recent Trades</h4>
            </div>
            <div className="p-4 flex-1 space-y-4 overflow-y-auto max-h-[500px]">
              <p className="text-sm text-[#49879c] text-center py-8">No recent trades</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}

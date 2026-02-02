'use client';

import { useQuery } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { adminApi, BroadcastHistoryItem } from '@/lib/api';
import { useRequireAdmin } from '@/hooks/useAuth';
import { format } from 'date-fns';
import Link from 'next/link';

export default function AdminBroadcastHistoryPage() {
  const { user, loading } = useRequireAdmin();

  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['broadcast-history'],
    queryFn: () => adminApi.getBroadcastHistory(),
    enabled: !loading,
    refetchInterval: 30000,
  });

  const columns = [
    {
      key: 'id',
      header: 'ID',
      render: (item: BroadcastHistoryItem) => <span className="font-semibold">#{item.id}</span>,
    },
    {
      key: 'symbol',
      header: 'Symbol',
      render: (item: BroadcastHistoryItem) => <span className="font-bold">{item.symbol}</span>,
    },
    {
      key: 'expiry',
      header: 'Expiry',
      render: (item: BroadcastHistoryItem) => format(new Date(item.expiry), 'dd-MMM-yyyy'),
    },
    {
      key: 'strike',
      header: 'Strike',
      render: (item: BroadcastHistoryItem) => item.strike,
    },
    {
      key: 'option_type',
      header: 'Type',
      render: (item: BroadcastHistoryItem) => (
        <span
          className={`px-2 py-1 rounded text-xs font-bold ${
            item.option_type === 'CE'
              ? 'bg-emerald-100 text-emerald-700'
              : 'bg-rose-100 text-rose-700'
          }`}
        >
          {item.option_type}
        </span>
      ),
    },
    {
      key: 'side',
      header: 'Side',
      render: (item: BroadcastHistoryItem) => (
        <span
          className={`px-2 py-1 rounded text-xs font-bold ${
            item.side === 'BUY'
              ? 'bg-blue-100 text-blue-700'
              : 'bg-orange-100 text-orange-700'
          }`}
        >
          {item.side}
        </span>
      ),
    },
    {
      key: 'created_at',
      header: 'Created At',
      render: (item: BroadcastHistoryItem) => format(new Date(item.created_at), 'PPpp'),
    },
    {
      key: 'total_users',
      header: 'Users',
      render: (item: BroadcastHistoryItem) => item.total_users,
    },
    {
      key: 'successful_executions',
      header: 'Success',
      render: (item: BroadcastHistoryItem) => (
        <span className="text-emerald-600 font-semibold">{item.successful_executions}</span>
      ),
    },
    {
      key: 'failed_executions',
      header: 'Failed',
      render: (item: BroadcastHistoryItem) => (
        <span className="text-rose-600 font-semibold">{item.failed_executions}</span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      align: 'center' as const,
      render: (item: BroadcastHistoryItem) => (
        <Link href={`/admin/broadcast/${item.id}`}>
          <button className="text-primary hover:underline text-sm font-medium">View Details</button>
        </Link>
      ),
    },
  ];

  if (loading || historyLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading history...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <TopNavbar
        title="Broadcast History"
        actions={
          <Link href="/admin/broadcast">
            <Button variant="primary" icon="add_circle">
              New Broadcast
            </Button>
          </Link>
        }
      />
      <div className="p-8">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-[#0d181c] dark:text-white mb-2">Broadcast History</h2>
          <p className="text-[#49879c]">View all past broadcast orders and their execution results</p>
        </div>

        <DataTable
          columns={columns}
          data={history || []}
          loading={historyLoading}
          emptyMessage="No broadcast history found"
        />
      </div>
    </Layout>
  );
}

'use client';

import { useQuery } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { DataTable } from '@/components/ui/DataTable';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { Button } from '@/components/ui/Button';
import { adminApi, AdminUser } from '@/lib/api';
import { useRequireAdmin } from '@/hooks/useAuth';
import Link from 'next/link';
import { format } from 'date-fns';

export default function AdminDashboardPage() {
  const { user, loading } = useRequireAdmin();

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.getUsers(),
    enabled: !loading,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const columns = [
    {
      key: 'email',
      header: 'Email',
      render: (user: AdminUser) => <span className="font-semibold">{user.email}</span>,
    },
    {
      key: 'role',
      header: 'Role',
      render: (user: AdminUser) => <StatusBadge status={user.role === 'ADMIN' ? 'ACTIVE' : 'PENDING'} />,
    },
    {
      key: 'broker_account',
      header: 'Broker',
      render: (user: AdminUser) =>
        user.broker_account ? (
          <span className="text-sm">{user.broker_account.broker_type}</span>
        ) : (
          <span className="text-sm text-[#49879c]">Not linked</span>
        ),
    },
    {
      key: 'token_status',
      header: 'Token Status',
      render: (user: AdminUser) =>
        user.token_status ? (
          <StatusBadge status={user.token_status.status} />
        ) : (
          <span className="text-sm text-[#49879c]">N/A</span>
        ),
    },
    {
      key: 'actions',
      header: 'Actions',
      align: 'center' as const,
      render: (user: AdminUser) => (
        <Link href={`/admin/users/${user.id}`}>
          <Button variant="ghost" size="sm">
            View
          </Button>
        </Link>
      ),
    },
  ];

  if (loading || usersLoading) {
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

  return (
    <Layout>
      <TopNavbar
        title="Admin Overview"
        showSearch
        searchPlaceholder="Search accounts, emails or brokers..."
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
          <h2 className="text-2xl font-bold text-[#0d181c] dark:text-white mb-2">User Management</h2>
          <p className="text-[#49879c]">Manage all user accounts and their broker connections</p>
        </div>

        <DataTable
          columns={columns}
          data={users || []}
          loading={usersLoading}
          emptyMessage="No users found"
        />
      </div>
    </Layout>
  );
}

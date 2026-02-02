'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { adminApi, BroadcastOrderRequest, AdminUser } from '@/lib/api';
import { useRequireAdmin } from '@/hooks/useAuth';
import { useForm } from 'react-hook-form';
import { useState } from 'react';

export default function AdminBroadcastOrderPage() {
  const { user, loading } = useRequireAdmin();
  const queryClient = useQueryClient();
  const [selectedUsers, setSelectedUsers] = useState<number[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [broadcastResult, setBroadcastResult] = useState<any>(null);

  const { data: users } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.getUsers(),
    enabled: !loading,
  });

  const broadcastMutation = useMutation({
    mutationFn: (data: BroadcastOrderRequest) => adminApi.broadcastOrder(data),
    onSuccess: (result) => {
      setBroadcastResult(result);
      setShowResults(true);
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<BroadcastOrderRequest>({
    defaultValues: {
      symbol: 'BANKNIFTY',
      execution_type: 'MARKET',
      product_type: 'MIS',
      broadcast_type: 'ENTRY',
      selected_user_ids: [],
      include_admin: false,
    },
  });

  const executionType = watch('execution_type');
  const broadcastType = watch('broadcast_type');

  const onSubmit = (data: BroadcastOrderRequest) => {
    if (selectedUsers.length === 0 && !data.include_admin) {
      alert('Please select at least one user or include admin account');
      return;
    }

    broadcastMutation.mutate({
      ...data,
      selected_user_ids: selectedUsers,
    });
  };

  const toggleUser = (userId: number) => {
    setSelectedUsers((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const readyUsers = users?.filter(
    (u) => u.broker_account && u.token_status?.status === 'ACTIVE'
  ) || [];

  return (
    <Layout>
      <TopNavbar title="Broadcast New Order" />
      <div className="p-8 max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-black text-[#0d181c] dark:text-white tracking-tight mb-2">
            Broadcast New Order
          </h1>
          <p className="text-slate-500 dark:text-slate-400 max-w-2xl">
            Configure your trade parameters and select target user accounts for simultaneous execution across
            multiple broker environments.
          </p>
        </div>

        {showResults && broadcastResult && (
          <div className="mb-6 bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
            <h3 className="text-lg font-bold mb-4">Broadcast Results</h3>
            <div className="space-y-2">
              <p>
                <span className="font-semibold">Total Users:</span> {broadcastResult.total_users}
              </p>
              <p>
                <span className="font-semibold text-emerald-600">Successful:</span>{' '}
                {broadcastResult.successful_executions}
              </p>
              <p>
                <span className="font-semibold text-rose-600">Failed:</span>{' '}
                {broadcastResult.failed_executions}
              </p>
              <p>
                <span className="font-semibold text-yellow-600">Skipped:</span>{' '}
                {broadcastResult.skipped_executions}
              </p>
            </div>
            <Button variant="primary" className="mt-4" onClick={() => setShowResults(false)}>
              Close
            </Button>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Order Configuration */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">settings_input_component</span>
                1. Order Configuration
              </h2>

              <div className="space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <Select
                    label="Symbol"
                    options={[
                      { value: 'BANKNIFTY', label: 'BANKNIFTY' },
                      { value: 'NIFTY', label: 'NIFTY' },
                      { value: 'SENSEX', label: 'SENSEX' },
                    ]}
                    {...register('symbol', { required: 'Symbol is required' })}
                    error={errors.symbol?.message}
                  />
                  <div>
                    <label className="block text-sm font-semibold mb-2">Broadcast Type</label>
                    <div className="grid grid-cols-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
                      <button
                        type="button"
                        className={`py-1.5 text-xs font-bold rounded-md ${
                          broadcastType === 'ENTRY'
                            ? 'bg-primary text-white shadow-sm'
                            : 'text-slate-500 dark:text-slate-400'
                        }`}
                        onClick={() => {
                          // This would need to be handled with form state
                        }}
                      >
                        ENTRY
                      </button>
                      <button
                        type="button"
                        className={`py-1.5 text-xs font-bold rounded-md ${
                          broadcastType === 'EXIT'
                            ? 'bg-primary text-white shadow-sm'
                            : 'text-slate-500 dark:text-slate-400'
                        }`}
                      >
                        EXIT
                      </button>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <Input
                    label="Expiry"
                    type="date"
                    {...register('expiry', { required: 'Expiry is required' })}
                    error={errors.expiry?.message}
                  />
                  <Input
                    label="Strike"
                    type="number"
                    {...register('strike', {
                      required: 'Strike is required',
                      valueAsNumber: true,
                    })}
                    error={errors.strike?.message}
                  />
                  <div>
                    <label className="block text-sm font-semibold mb-2">Type</label>
                    <Select
                      options={[
                        { value: 'CE', label: 'CE' },
                        { value: 'PE', label: 'PE' },
                      ]}
                      {...register('option_type', { required: 'Option type is required' })}
                      error={errors.option_type?.message}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">Side</label>
                    <Select
                      options={[
                        { value: 'BUY', label: 'BUY' },
                        { value: 'SELL', label: 'SELL' },
                      ]}
                      {...register('side', { required: 'Side is required' })}
                      error={errors.side?.message}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2">Execution</label>
                    <Select
                      options={[
                        { value: 'MARKET', label: 'MARKET' },
                        { value: 'LIMIT', label: 'LIMIT' },
                      ]}
                      {...register('execution_type', { required: 'Execution type is required' })}
                      error={errors.execution_type?.message}
                    />
                  </div>
                </div>

                {executionType === 'LIMIT' && (
                  <Input
                    label="Limit Price"
                    type="number"
                    step="0.01"
                    {...register('limit_price', {
                      required: 'Limit price is required for LIMIT orders',
                      valueAsNumber: true,
                    })}
                    error={errors.limit_price?.message}
                  />
                )}

                <Input
                  label="Notes (Optional)"
                  {...register('notes')}
                  error={errors.notes?.message}
                />
              </div>
            </div>
          </div>

          {/* User Selection */}
          <div className="lg:col-span-7">
            <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <span className="material-symbols-outlined text-primary">group</span>
                2. Select Users
              </h2>

              <div className="mb-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    {...register('include_admin')}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm font-medium">Include my account (Admin)</span>
                </label>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {readyUsers.map((u) => (
                  <label
                    key={u.id}
                    className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer border border-transparent hover:border-primary/20"
                  >
                    <input
                      type="checkbox"
                      checked={selectedUsers.includes(u.id)}
                      onChange={() => toggleUser(u.id)}
                      className="rounded border-gray-300"
                    />
                    <div className="flex-1">
                      <p className="font-semibold text-sm">{u.email}</p>
                      <p className="text-xs text-[#49879c]">
                        {u.broker_account?.broker_type} • Token: Active
                      </p>
                    </div>
                  </label>
                ))}
              </div>

              {readyUsers.length === 0 && (
                <p className="text-sm text-[#49879c] text-center py-8">
                  No users with active broker accounts available
                </p>
              )}

              <div className="mt-6 pt-6 border-t border-[#cee2e8] dark:border-gray-800">
                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full"
                  disabled={broadcastMutation.isPending}
                >
                  {broadcastMutation.isPending ? 'Broadcasting...' : 'Broadcast Order'}
                </Button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </Layout>
  );
}

'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { brokerApi, BrokerAccount, BrokerAccountCreate } from '@/lib/api';
import { useRequireAuth } from '@/hooks/useAuth';
import { useForm } from 'react-hook-form';
import { useState, useEffect } from 'react';
import { format, differenceInSeconds, formatDuration, intervalToDuration } from 'date-fns';

export default function BrokerAccountPage() {
  const { user, loading } = useRequireAuth();
  const queryClient = useQueryClient();
  const [showAddForm, setShowAddForm] = useState(false);
  const [tokenCountdown, setTokenCountdown] = useState<string>('');

  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ['broker-accounts'],
    queryFn: () => brokerApi.getBrokerAccounts(),
    enabled: !loading,
  });

  const account = accounts && accounts.length > 0 ? accounts[0] : null;

  // Token countdown timer
  useEffect(() => {
    if (account?.token_expires_at) {
      const updateCountdown = () => {
        const expiresAt = new Date(account.token_expires_at!);
        const now = new Date();
        const diff = differenceInSeconds(expiresAt, now);

        if (diff > 0) {
          const duration = intervalToDuration({ start: 0, end: diff * 1000 });
          const hours = String(duration.hours || 0).padStart(2, '0');
          const minutes = String(duration.minutes || 0).padStart(2, '0');
          const seconds = String(duration.seconds || 0).padStart(2, '0');
          setTokenCountdown(`${hours}:${minutes}:${seconds}`);
        } else {
          setTokenCountdown('EXPIRED');
        }
      };

      updateCountdown();
      const interval = setInterval(updateCountdown, 1000);
      return () => clearInterval(interval);
    }
  }, [account?.token_expires_at]);

  const linkMutation = useMutation({
    mutationFn: (data: BrokerAccountCreate) => brokerApi.linkBrokerAccount(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['broker-accounts'] });
      setShowAddForm(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (accountId: number) => brokerApi.deleteBrokerAccount(accountId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['broker-accounts'] });
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<BrokerAccountCreate & { api_secret?: string }>({
    defaultValues: {
      broker_type: 'ZERODHA',
    },
  });

  const brokerType = watch('broker_type');

  const onSubmit = (data: BrokerAccountCreate & { api_secret?: string }) => {
    linkMutation.mutate({
      broker_type: data.broker_type,
      api_key: data.api_key,
      api_secret: data.api_secret,
      client_id: data.client_id,
    });
  };

  const handleGenerateToken = async () => {
    if (!account) return;

    if (account.broker_type === 'ZERODHA') {
      try {
        const { login_url } = await brokerApi.generateZerodhaLoginUrl(account.id);
        window.open(login_url, '_blank', 'width=600,height=700');
      } catch (error: any) {
        alert(`Error: ${error.message}`);
      }
    } else if (account.broker_type === 'DHAN') {
      try {
        const { consent_url } = await brokerApi.generateDhanConsent(account.id);
        window.open(consent_url, '_blank', 'width=600,height=700');
      } catch (error: any) {
        alert(`Error: ${error.message}`);
      }
    }
  };

  if (loading || accountsLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading broker account...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <TopNavbar title="Broker Management" />
      <div className="p-8 max-w-6xl w-full mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <h2 className="text-2xl font-bold text-[#0d181c] dark:text-white">Broker Account</h2>
            <p className="text-sm text-[#49879c] mt-1">Manage your broker account connections</p>
          </div>
          {!account && (
            <Button variant="primary" onClick={() => setShowAddForm(true)} icon="add">
              Add Broker Account
            </Button>
          )}
        </div>

        {showAddForm && !account && (
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 mb-6">
            <h3 className="text-lg font-bold mb-4">Link Broker Account</h3>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Select
                label="Broker Type"
                options={[
                  { value: 'ZERODHA', label: 'Zerodha' },
                  { value: 'DHAN', label: 'Dhan' },
                ]}
                {...register('broker_type', { required: 'Broker type is required' })}
                error={errors.broker_type?.message}
              />

              {brokerType === 'ZERODHA' && (
                <>
                  <Input
                    label="API Key"
                    placeholder="Enter your Zerodha API key"
                    {...register('api_key', { required: 'API key is required' })}
                    error={errors.api_key?.message}
                  />
                  <Input
                    label="API Secret"
                    type="password"
                    placeholder="Enter your Zerodha API secret"
                    {...register('api_secret', { required: 'API secret is required' })}
                    error={errors.api_secret?.message}
                  />
                </>
              )}

              {brokerType === 'DHAN' && (
                <Input
                  label="Client ID"
                  placeholder="Enter your Dhan Client ID"
                  {...register('client_id', { required: 'Client ID is required' })}
                  error={errors.client_id?.message}
                />
              )}

              <div className="flex justify-end gap-4">
                <Button type="button" variant="secondary" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={linkMutation.isPending}>
                  {linkMutation.isPending ? 'Linking...' : 'Link Account'}
                </Button>
              </div>
            </form>
          </div>
        )}

        {account && (
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-xl font-bold text-[#0d181c] dark:text-white mb-2">
                  {account.broker_type} Account
                </h3>
                <StatusBadge status={account.status} />
              </div>
              <Button variant="danger" size="sm" onClick={() => deleteMutation.mutate(account.id)}>
                Remove Account
              </Button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-[#49879c] mb-1">Broker Type</p>
                  <p className="font-semibold">{account.broker_type}</p>
                </div>
                <div>
                  <p className="text-sm text-[#49879c] mb-1">Status</p>
                  <StatusBadge status={account.status} />
                </div>
              </div>

              {account.token_expires_at && (
                <div>
                  <p className="text-sm text-[#49879c] mb-1">Token Expires At</p>
                  <p className="font-semibold">{format(new Date(account.token_expires_at), 'PPpp')}</p>
                  {tokenCountdown && (
                    <p className="text-sm text-primary mt-1">Time remaining: {tokenCountdown}</p>
                  )}
                </div>
              )}

              <div className="pt-4 border-t border-[#cee2e8] dark:border-gray-800">
                <Button variant="primary" onClick={handleGenerateToken} icon="key">
                  Generate Token
                </Button>
                <p className="text-xs text-[#49879c] mt-2">
                  Click to generate and set your broker access token
                </p>
              </div>
            </div>
          </div>
        )}

        {!account && !showAddForm && (
          <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-12 text-center">
            <span className="material-symbols-outlined text-6xl text-[#49879c] mb-4">account_balance_wallet</span>
            <h3 className="text-xl font-bold text-[#0d181c] dark:text-white mb-2">No Broker Account</h3>
            <p className="text-[#49879c] mb-6">Link your broker account to start copy trading</p>
            <Button variant="primary" onClick={() => setShowAddForm(true)} icon="add">
              Add Broker Account
            </Button>
          </div>
        )}
      </div>
    </Layout>
  );
}

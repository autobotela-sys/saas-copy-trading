'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { userApi, TradingProfile } from '@/lib/api';
import { useRequireAuth } from '@/hooks/useAuth';
import { useForm } from 'react-hook-form';
import { useState } from 'react';

export default function TradingProfilePage() {
  const { user, loading } = useRequireAuth();
  const queryClient = useQueryClient();
  const [successMessage, setSuccessMessage] = useState('');

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['trading-profile'],
    queryFn: () => userApi.getTradingProfile(),
    enabled: !loading,
  });

  const updateMutation = useMutation({
    mutationFn: (data: TradingProfile) => userApi.updateTradingProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['trading-profile'] });
      setSuccessMessage('Trading profile updated successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
    },
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<TradingProfile>({
    defaultValues: profile || {
      lot_size_multiplier: 'ONE_X',
      risk_profile: 'MODERATE',
    },
    values: profile,
  });

  const onSubmit = (data: TradingProfile) => {
    updateMutation.mutate(data);
  };

  if (loading || profileLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading profile...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <TopNavbar title="Trading Profile Settings" />
      <div className="p-8 max-w-4xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-black text-[#0d181c] dark:text-white tracking-tight">
            My Trading Profile
          </h2>
          <p className="text-slate-500 dark:text-slate-400 mt-2 text-base">
            Configure your copy trading parameters and risk management settings.
          </p>
        </div>

        {successMessage && (
          <div className="mb-6 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 px-4 py-3 rounded-lg text-sm">
            {successMessage}
          </div>
        )}

        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm overflow-hidden">
          <div className="p-6 lg:p-8">
            <h3 className="text-xl font-bold text-[#0d181c] dark:text-white mb-6 flex items-center gap-2">
              <span className="material-symbols-outlined text-primary">analytics</span>
              Copy Trading Configuration
            </h3>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
              <div>
                <Select
                  label="Lot Size Multiplier"
                  options={[
                    { value: 'ONE_X', label: '1X (Standard)' },
                    { value: 'TWO_X', label: '2X (Double)' },
                    { value: 'THREE_X', label: '3X (Triple)' },
                  ]}
                  {...register('lot_size_multiplier', { required: 'Multiplier is required' })}
                  error={errors.lot_size_multiplier?.message}
                />
                <div className="mt-3 flex gap-3 p-4 bg-primary/5 dark:bg-primary/10 border border-primary/20 rounded-lg">
                  <span className="material-symbols-outlined text-primary text-[20px]">info</span>
                  <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                    <span className="font-medium text-slate-900 dark:text-slate-200">Example:</span> If admin
                    broadcasts 1 lot of BANKNIFTY (30 qty) and you set 2X, you will trade 60 qty.
                  </p>
                </div>
              </div>

              <div>
                <Select
                  label="Risk Profile"
                  options={[
                    { value: 'CONSERVATIVE', label: 'Conservative' },
                    { value: 'MODERATE', label: 'Moderate' },
                    { value: 'AGGRESSIVE', label: 'Aggressive' },
                  ]}
                  {...register('risk_profile', { required: 'Risk profile is required' })}
                  error={errors.risk_profile?.message}
                />
              </div>

              <div className="flex justify-end gap-4 pt-4 border-t border-[#cee2e8] dark:border-gray-800">
                <Button type="button" variant="secondary" onClick={() => window.history.back()}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={updateMutation.isPending}>
                  {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </Layout>
  );
}

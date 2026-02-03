'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { userApi, authApi, User } from '@/lib/api';
import { useRequireAuth } from '@/hooks/useAuth';
import { format } from 'date-fns';
import { logout } from '@/lib/auth';
import Link from 'next/link';

export default function ProfilePage() {
  const { user, loading } = useRequireAuth();
  const queryClient = useQueryClient();

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['user-profile'],
    queryFn: () => userApi.getProfile(),
    enabled: !loading,
  });

  const refreshUser = async () => {
    await queryClient.invalidateQueries({ queryKey: ['user-profile'] });
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

  const currentUser = profile || user;

  return (
    <Layout>
      <TopNavbar title="My Profile" />
      <div className="p-8 max-w-4xl mx-auto">
        {/* Profile Header */}
        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm overflow-hidden mb-6">
          <div className="bg-gradient-to-r from-primary to-blue-600 h-32"></div>
          <div className="px-6 pb-6">
            <div className="flex items-end -mt-12 mb-4">
              <div className="w-24 h-24 bg-white dark:bg-gray-800 rounded-full border-4 border-white dark:border-gray-800 flex items-center justify-center shadow-lg">
                <span className="material-symbols-outlined text-5xl text-primary">person</span>
              </div>
              <div className="ml-4 mb-2">
                <h2 className="text-2xl font-bold text-[#0d181c] dark:text-white">{currentUser?.email}</h2>
                <p className="text-[#49879c]">{currentUser?.role} Account</p>
              </div>
            </div>
          </div>
        </div>

        {/* Account Information */}
        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 mb-6">
          <h3 className="text-lg font-bold text-[#0d181c] dark:text-white mb-4 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">account_circle</span>
            Account Information
          </h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-[#49879c] mb-1">Email Address</p>
                <p className="font-semibold">{currentUser?.email}</p>
              </div>
              <div>
                <p className="text-sm text-[#49879c] mb-1">Role</p>
                <p className="font-semibold">{currentUser?.role}</p>
              </div>
              <div>
                <p className="text-sm text-[#49879c] mb-1">Status</p>
                <StatusBadge status={currentUser?.status || 'ACTIVE'} />
              </div>
              <div>
                <p className="text-sm text-[#49879c] mb-1">Email Verified</p>
                <p className="font-semibold">
                  {currentUser?.status === 'ACTIVE' ? (
                    <span className="text-emerald-600">Verified</span>
                  ) : (
                    <span className="text-amber-600">Pending</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 mb-6">
          <h3 className="text-lg font-bold text-[#0d181c] dark:text-white mb-4 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">settings</span>
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link href="/profile/trading">
              <div className="flex items-center gap-3 p-4 rounded-lg border border-[#cee2e8] dark:border-gray-700 hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-primary">analytics</span>
                <div>
                  <p className="font-semibold">Trading Settings</p>
                  <p className="text-sm text-[#49879c]">Lot size & risk profile</p>
                </div>
              </div>
            </Link>
            <Link href="/profile/broker">
              <div className="flex items-center gap-3 p-4 rounded-lg border border-[#cee2e8] dark:border-gray-700 hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-primary">account_balance_wallet</span>
                <div>
                  <p className="font-semibold">Broker Account</p>
                  <p className="text-sm text-[#49879c]">Manage broker connections</p>
                </div>
              </div>
            </Link>
            <Link href="/notifications">
              <div className="flex items-center gap-3 p-4 rounded-lg border border-[#cee2e8] dark:border-gray-700 hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-primary">notifications</span>
                <div>
                  <p className="font-semibold">Notifications</p>
                  <p className="text-sm text-[#49879c]">View your notifications</p>
                </div>
              </div>
            </Link>
            <Link href="/support">
              <div className="flex items-center gap-3 p-4 rounded-lg border border-[#cee2e8] dark:border-gray-700 hover:border-primary hover:bg-primary/5 transition-colors cursor-pointer">
                <span className="material-symbols-outlined text-primary">support_agent</span>
                <div>
                  <p className="font-semibold">Help & Support</p>
                  <p className="text-sm text-[#49879c]">Get help with your account</p>
                </div>
              </div>
            </Link>
          </div>
        </div>

        {/* Security */}
        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
          <h3 className="text-lg font-bold text-[#0d181c] dark:text-white mb-4 flex items-center gap-2">
            <span className="material-symbols-outlined text-primary">security</span>
            Security
          </h3>
          <div className="space-y-3">
            <Link href="/forgot-password">
              <Button variant="secondary" className="w-full justify-start" icon="lock">
                Change Password
              </Button>
            </Link>
            <Button
              variant="danger"
              className="w-full justify-start"
              icon="logout"
              onClick={logout}
            >
              Logout
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
}

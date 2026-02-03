'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { userApi } from '@/lib/api';
import { useRequireAuth } from '@/hooks/useAuth';
import { format } from 'date-fns';
import { useState } from 'react';

// Mock notification types (these would come from backend)
interface Notification {
  id: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  title: string;
  message: string;
  created_at: string;
  read: boolean;
}

export default function NotificationsPage() {
  const { user, loading } = useRequireAuth();
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');

  // Mock notifications data - in production, this would come from API
  const mockNotifications: Notification[] = [
    {
      id: '1',
      type: 'SUCCESS',
      title: 'Position Closed',
      message: 'Your BANKNIFTY 25000 CE position has been closed with profit of ₹2,450.',
      created_at: new Date(Date.now() - 3600000).toISOString(),
      read: false,
    },
    {
      id: '2',
      type: 'WARNING',
      title: 'Token Expiring Soon',
      message: 'Your broker access token will expire in less than 1 hour. Please refresh it.',
      created_at: new Date(Date.now() - 7200000).toISOString(),
      read: false,
    },
    {
      id: '3',
      type: 'INFO',
      title: 'New Broadcast Order',
      message: 'Admin has broadcasted a new NIFTY order. Check your positions.',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      read: true,
    },
    {
      id: '4',
      type: 'ERROR',
      title: 'Order Failed',
      message: 'Your order for BANKNIFTY 24800 PE failed due to insufficient margin.',
      created_at: new Date(Date.now() - 172800000).toISOString(),
      read: true,
    },
  ];

  const filteredNotifications = mockNotifications.filter((n) => {
    if (filter === 'unread') return !n.read;
    if (filter === 'read') return n.read;
    return true;
  });

  const markAsRead = (id: string) => {
    // In production, call API to mark as read
    console.log('Mark as read:', id);
  };

  const markAllAsRead = () => {
    // In production, call API to mark all as read
    console.log('Mark all as read');
  };

  const deleteNotification = (id: string) => {
    // In production, call API to delete
    console.log('Delete notification:', id);
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'SUCCESS': return 'check_circle';
      case 'WARNING': return 'warning';
      case 'ERROR': return 'error';
      default: return 'info';
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case 'SUCCESS': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20';
      case 'WARNING': return 'text-amber-600 bg-amber-50 dark:bg-amber-900/20';
      case 'ERROR': return 'text-rose-600 bg-rose-50 dark:bg-rose-900/20';
      default: return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20';
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading notifications...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const unreadCount = mockNotifications.filter((n) => !n.read).length;

  return (
    <Layout>
      <TopNavbar
        title="Notifications"
        actions={
          unreadCount > 0 && (
            <Button variant="secondary" size="sm" onClick={markAllAsRead}>
              Mark All Read
            </Button>
          )
        }
      />
      <div className="p-8 max-w-4xl mx-auto">
        {/* Filters */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={filter === 'all' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilter('all')}
          >
            All ({mockNotifications.length})
          </Button>
          <Button
            variant={filter === 'unread' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilter('unread')}
          >
            Unread ({unreadCount})
          </Button>
          <Button
            variant={filter === 'read' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilter('read')}
          >
            Read ({mockNotifications.length - unreadCount})
          </Button>
        </div>

        {/* Notifications List */}
        <div className="space-y-4">
          {filteredNotifications.length === 0 ? (
            <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-12 text-center">
              <span className="material-symbols-outlined text-6xl text-[#49879c] mb-4">notifications_none</span>
              <h3 className="text-xl font-bold text-[#0d181c] dark:text-white mb-2">No Notifications</h3>
              <p className="text-[#49879c]">You're all caught up!</p>
            </div>
          ) : (
            filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`bg-white dark:bg-background-dark rounded-xl border ${
                  notification.read ? 'border-[#cee2e8] dark:border-gray-800 opacity-70' : 'border-primary dark:border-primary'
                } shadow-sm p-4 hover:shadow-md transition-shadow`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-2 rounded-full ${getNotificationColor(notification.type)}`}>
                    <span className="material-symbols-outlined">{getNotificationIcon(notification.type)}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h4 className="font-semibold text-[#0d181c] dark:text-white flex items-center gap-2">
                          {notification.title}
                          {!notification.read && (
                            <span className="w-2 h-2 bg-primary rounded-full"></span>
                          )}
                        </h4>
                        <p className="text-sm text-[#49879c] mt-1">{notification.message}</p>
                        <p className="text-xs text-[#49879c] mt-2">
                          {format(new Date(notification.created_at), 'PPpp')}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        {!notification.read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => markAsRead(notification.id)}
                            title="Mark as read"
                          >
                            <span className="material-symbols-outlined text-lg">check</span>
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteNotification(notification.id)}
                          title="Delete"
                        >
                          <span className="material-symbols-outlined text-lg">delete</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Notification Preferences */}
        <div className="mt-8 bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
          <h3 className="text-lg font-bold text-[#0d181c] dark:text-white mb-4">Notification Preferences</h3>
          <div className="space-y-4">
            <label className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
              <div>
                <p className="font-semibold">Email Notifications</p>
                <p className="text-sm text-[#49879c]">Receive notifications via email</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary" />
            </label>
            <label className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
              <div>
                <p className="font-semibold">Trade Alerts</p>
                <p className="text-sm text-[#49879c]">Get notified for every trade execution</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary" />
            </label>
            <label className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer">
              <div>
                <p className="font-semibold">Token Expiry Reminders</p>
                <p className="text-sm text-[#49879c]">Remind before broker token expires</p>
              </div>
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary" />
            </label>
          </div>
        </div>
      </div>
    </Layout>
  );
}

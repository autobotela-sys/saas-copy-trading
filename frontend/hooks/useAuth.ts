'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAuthToken, getUser, isAuthenticated, isAdmin, refreshUser, User } from '@/lib/auth';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const initAuth = async () => {
      if (isAuthenticated()) {
        const currentUser = getUser();
        if (currentUser) {
          setUser(currentUser);
          // Refresh user data in background
          refreshUser().then((updatedUser) => {
            if (updatedUser) setUser(updatedUser);
          });
        } else {
          // Try to refresh from API
          const refreshedUser = await refreshUser();
          setUser(refreshedUser);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  return {
    user,
    loading,
    isAuthenticated: isAuthenticated(),
    isAdmin: isAdmin(),
  };
}

export function useRequireAuth() {
  const { user, loading, isAuthenticated } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/login');
    }
  }, [loading, isAuthenticated, router]);

  return { user, loading };
}

export function useRequireAdmin() {
  const { user, loading, isAuthenticated, isAdmin: userIsAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && (!isAuthenticated || !userIsAdmin)) {
      router.push('/dashboard');
    }
  }, [loading, isAuthenticated, userIsAdmin, router]);

  return { user, loading };
}

'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Layout } from '@/components/layout/Layout';
import { TopNavbar } from '@/components/layout/TopNavbar';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { userApi, Position } from '@/lib/api';
import { useRequireAuth } from '@/hooks/useAuth';
import { useRouter, useParams } from 'next/navigation';
import { useState } from 'react';
import { format } from 'date-fns';

export default function ClosePositionPage() {
  const { user, loading } = useRequireAuth();
  const router = useRouter();
  const params = useParams();
  const positionId = parseInt(params.id as string);

  const queryClient = useQueryClient();
  const [exitPrice, setExitPrice] = useState<number | ''>('');
  const [exitQuantity, setExitQuantity] = useState<number | ''>('');
  const [showFullClose, setShowFullClose] = useState(true);

  // Fetch the specific position
  const { data: allPositions, isLoading: positionsLoading } = useQuery({
    queryKey: ['positions', 'OPEN'],
    queryFn: () => userApi.getPositions('OPEN'),
    enabled: !loading && !isNaN(positionId),
  });

  const position = allPositions?.find((p: Position) => p.id === positionId);

  const closeMutation = useMutation({
    mutationFn: (data: { exitPrice: number; exitQuantity?: number }) =>
      userApi.closePosition(positionId, data.exitPrice, data.exitQuantity),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      // Show success and redirect
      alert(`Position closed successfully! P&L: ${result.pnl}`);
      router.push('/dashboard');
    },
    onError: (error: Error) => {
      alert(`Failed to close position: ${error.message}`);
    },
  });

  if (loading || positionsLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-[#49879c]">Loading position...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!position) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Position Not Found</h2>
            <p className="text-[#49879c] mb-6">The position you're looking for doesn't exist or has already been closed.</p>
            <Button variant="primary" onClick={() => router.push('/dashboard')}>
              Back to Dashboard
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  const handleFullClose = () => {
    if (position.current_price) {
      closeMutation.mutate({
        exitPrice: position.current_price,
      });
    }
  };

  const handlePartialClose = () => {
    if (typeof exitPrice === 'number' && typeof exitQuantity === 'number') {
      if (exitQuantity <= 0 || exitQuantity > position.quantity) {
        alert('Invalid quantity');
        return;
      }
      closeMutation.mutate({
        exitPrice,
        exitQuantity,
      });
    } else {
      alert('Please enter valid exit price and quantity');
    }
  };

  return (
    <Layout>
      <TopNavbar title="Close Position" />
      <div className="p-8 max-w-4xl mx-auto">
        {/* Position Details */}
        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-[#0d181c] dark:text-white mb-4">Position Details</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-[#49879c] mb-1">Symbol</p>
              <p className="font-semibold">{position.symbol}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Expiry</p>
              <p className="font-semibold">{format(new Date(position.expiry), 'dd-MMM-yyyy')}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Strike</p>
              <p className="font-semibold">{position.strike}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Type</p>
              <span
                className={`px-2 py-1 rounded text-xs font-bold ${
                  position.option_type === 'CE'
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-rose-100 text-rose-700'
                }`}
              >
                {position.option_type}
              </span>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Side</p>
              <p className="font-semibold">{position.side}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Quantity</p>
              <p className="font-semibold">{position.quantity}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Entry Price</p>
              <p className="font-semibold">₹{position.entry_price.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Current Price</p>
              <p className="font-semibold">₹{position.current_price?.toFixed(2) || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Current P&L</p>
              <p
                className={`font-bold ${
                  position.pnl >= 0 ? 'text-emerald-500' : 'text-rose-500'
                }`}
              >
                {position.pnl >= 0 ? '+' : ''}₹{position.pnl.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-[#49879c] mb-1">Status</p>
              <StatusBadge status={position.status} />
            </div>
          </div>
        </div>

        {/* Close Position Form */}
        <div className="bg-white dark:bg-background-dark rounded-xl border border-[#cee2e8] dark:border-gray-800 shadow-sm p-6">
          <h2 className="text-xl font-bold text-[#0d181c] dark:text-white mb-6">Close Position</h2>

          {/* Close Type Toggle */}
          <div className="mb-6">
            <div className="flex gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg w-fit">
              <button
                type="button"
                className={`px-4 py-2 rounded-md text-sm font-semibold transition-colors ${
                  showFullClose
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                }`}
                onClick={() => setShowFullClose(true)}
              >
                Full Close
              </button>
              <button
                type="button"
                className={`px-4 py-2 rounded-md text-sm font-semibold transition-colors ${
                  !showFullClose
                    ? 'bg-primary text-white shadow-sm'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700'
                }`}
                onClick={() => setShowFullClose(false)}
              >
                Partial Close
              </button>
            </div>
          </div>

          {showFullClose ? (
            /* Full Close */
            <div className="space-y-4">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <p className="text-sm text-blue-800 dark:text-blue-300">
                  <span className="font-semibold">Full Close:</span> You will close the entire position of{' '}
                  <span className="font-bold">{position.quantity} qty</span> at the current market price.
                </p>
              </div>

              <div className="flex items-center gap-4">
                <p className="text-sm text-[#49879c]">Estimated Exit Price:</p>
                <p className="font-semibold text-lg">₹{position.current_price?.toFixed(2) || 'N/A'}</p>
              </div>

              <div className="flex gap-4">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleFullClose}
                  disabled={closeMutation.isPending || !position.current_price}
                >
                  {closeMutation.isPending ? 'Closing...' : 'Close Full Position'}
                </Button>
                <Button variant="secondary" size="lg" onClick={() => router.push('/dashboard')}>
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            /* Partial Close */
            <div className="space-y-4">
              <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
                <p className="text-sm text-orange-800 dark:text-orange-300">
                  <span className="font-semibold">Partial Close:</span> Specify the quantity you want to close.
                  Remaining quantity will stay open.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold mb-2">Exit Price (₹)</label>
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="Enter exit price"
                    value={exitPrice}
                    onChange={(e) => setExitPrice(parseFloat(e.target.value) || '')}
                  />
                  <p className="text-xs text-[#49879c] mt-1">Current: ₹{position.current_price?.toFixed(2) || 'N/A'}</p>
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Exit Quantity</label>
                  <Input
                    type="number"
                    placeholder={`Max: ${position.quantity}`}
                    value={exitQuantity}
                    onChange={(e) => {
                      const val = parseInt(e.target.value) || '';
                      if (typeof val === 'number' && val <= position.quantity) {
                        setExitQuantity(val);
                      }
                    }}
                    max={position.quantity}
                    min={1}
                  />
                  <p className="text-xs text-[#49879c] mt-1">Max available: {position.quantity}</p>
                </div>
              </div>

              <div className="flex gap-4">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handlePartialClose}
                  disabled={closeMutation.isPending || !exitPrice || !exitQuantity}
                >
                  {closeMutation.isPending ? 'Closing...' : 'Close Partial Position'}
                </Button>
                <Button variant="secondary" size="lg" onClick={() => router.push('/dashboard')}>
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

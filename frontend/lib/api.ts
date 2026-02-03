// API client for FastAPI backend
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://backend-production-f8f2.up.railway.app';

// Types
export interface User {
  id: number;
  email: string;
  role: 'ADMIN' | 'USER';
  status: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserRegister {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TradingProfile {
  lot_size_multiplier: 'ONE_X' | 'TWO_X' | 'THREE_X';
  risk_profile: 'CONSERVATIVE' | 'MODERATE' | 'AGGRESSIVE';
}

export interface BrokerAccount {
  id: number;
  user_id: number;
  broker_type: 'ZERODHA' | 'DHAN';
  api_key?: string;
  status: 'ACTIVE' | 'INACTIVE' | 'PENDING';
  token_expires_at?: string;
  created_at: string;
}

export interface BrokerAccountCreate {
  broker_type: 'ZERODHA' | 'DHAN';
  api_key?: string;
  api_secret?: string;
  client_id?: string;
}

export interface TokenStatus {
  is_valid: boolean;
  expires_at?: string;
  time_remaining?: string;
  status: 'ACTIVE' | 'EXPIRED' | 'PENDING';
}

export interface DashboardData {
  total_pnl: number;
  today_pnl: number;
  open_positions_count: number;
  closed_positions_count: number;
  broker_account?: BrokerAccount;
  token_status?: TokenStatus;
}

export interface Position {
  id: number;
  symbol: string;
  expiry: string;
  strike: number;
  option_type: 'CE' | 'PE';
  side: 'BUY' | 'SELL';
  quantity: number;
  entry_price: number;
  current_price?: number;
  pnl: number;
  status: 'OPEN' | 'CLOSED';
  created_at: string;
  closed_at?: string;
}

export interface BroadcastOrderRequest {
  symbol: 'BANKNIFTY' | 'NIFTY' | 'SENSEX';
  expiry: string;
  strike: number;
  option_type: 'CE' | 'PE';
  side: 'BUY' | 'SELL';
  execution_type: 'MARKET' | 'LIMIT';
  limit_price?: number;
  product_type?: 'MIS' | 'NRML' | 'CNC';
  broadcast_type: 'ENTRY' | 'EXIT';
  selected_user_ids: number[];
  include_admin: boolean;
  notes?: string;
}

export interface BroadcastOrderResponse {
  id: number;
  symbol: string;
  expiry: string;
  strike: number;
  option_type: string;
  side: string;
  execution_type: string;
  limit_price?: number;
  product_type: string;
  broadcast_type: string;
  created_by: number;
  created_at: string;
  total_users: number;
  successful_executions: number;
  failed_executions: number;
  skipped_executions: number;
  execution_details: Array<{
    user_id: number;
    user_email: string;
    status: 'SUCCESS' | 'FAILED' | 'SKIPPED';
    message?: string;
    order_id?: string;
  }>;
}

export interface BroadcastHistoryItem {
  id: number;
  symbol: string;
  expiry: string;
  strike: number;
  option_type: string;
  side: string;
  execution_type: string;
  broadcast_type: string;
  created_at: string;
  total_users: number;
  successful_executions: number;
  failed_executions: number;
}

export interface AdminUser {
  id: number;
  email: string;
  role: string;
  status: string;
  broker_account?: BrokerAccount;
  trading_profile?: TradingProfile;
  token_status?: TokenStatus;
}

// Helper function to get auth token
const getAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
};

// Helper function to make API requests
const apiRequest = async <T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
};

// Auth endpoints
export const authApi = {
  register: async (data: UserRegister): Promise<User> => {
    return apiRequest<User>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  login: async (data: UserLogin): Promise<Token> => {
    return apiRequest<Token>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getCurrentUser: async (): Promise<User> => {
    return apiRequest<User>('/api/auth/me');
  },
};

// User endpoints
export const userApi = {
  getProfile: async (): Promise<User> => {
    return apiRequest<User>('/api/users/me');
  },

  getDashboard: async (): Promise<DashboardData> => {
    return apiRequest<DashboardData>('/api/users/me/dashboard');
  },

  getTradingProfile: async (): Promise<TradingProfile> => {
    return apiRequest<TradingProfile>('/api/users/me/trading-profile');
  },

  updateTradingProfile: async (data: TradingProfile): Promise<TradingProfile> => {
    return apiRequest<TradingProfile>('/api/users/me/trading-profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  getPositions: async (status?: 'OPEN' | 'CLOSED'): Promise<Position[]> => {
    const query = status ? `?status=${status}` : '';
    const response = await apiRequest<{positions: Position[]}>(`/api/users/me/positions${query}`);
    return response.positions;
  },

  closePosition: async (positionId: number, exitPrice: number, exitQuantity?: number): Promise<{
    position_id: number;
    status: string;
    remaining_quantity: number;
    pnl: number;
  }> => {
    return apiRequest<{
      position_id: number;
      status: string;
      remaining_quantity: number;
      pnl: number;
    }>(`/api/users/me/positions/${positionId}/close`, {
      method: 'POST',
      body: JSON.stringify({
        exit_price: exitPrice,
        exit_quantity: exitQuantity
      }),
    });
  },
};

// Broker endpoints
export const brokerApi = {
  getBrokerAccounts: async (): Promise<BrokerAccount[]> => {
    return apiRequest<BrokerAccount[]>('/api/users/broker-accounts');
  },

  linkBrokerAccount: async (data: BrokerAccountCreate): Promise<BrokerAccount> => {
    return apiRequest<BrokerAccount>('/api/users/broker-accounts', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  deleteBrokerAccount: async (accountId: number): Promise<void> => {
    return apiRequest<void>(`/api/users/broker-accounts/${accountId}`, {
      method: 'DELETE',
    });
  },

  getTokenStatus: async (accountId: number): Promise<TokenStatus> => {
    return apiRequest<TokenStatus>(`/api/users/broker-accounts/${accountId}/token-status`);
  },

  generateZerodhaLoginUrl: async (accountId: number): Promise<{ login_url: string }> => {
    return apiRequest<{ login_url: string }>(`/api/users/broker-accounts/${accountId}/zerodha/login-url`);
  },

  exchangeZerodhaToken: async (accountId: number, requestToken: string): Promise<BrokerAccount> => {
    return apiRequest<BrokerAccount>(`/api/users/broker-accounts/${accountId}/zerodha/exchange-token`, {
      method: 'POST',
      body: JSON.stringify({ request_token: requestToken }),
    });
  },

  generateDhanConsent: async (accountId: number): Promise<{ consent_url: string }> => {
    return apiRequest<{ consent_url: string }>(`/api/users/broker-accounts/${accountId}/dhan/generate-consent`);
  },

  exchangeDhanToken: async (accountId: number, authCode: string): Promise<BrokerAccount> => {
    return apiRequest<BrokerAccount>(`/api/users/broker-accounts/${accountId}/dhan/exchange-token`, {
      method: 'POST',
      body: JSON.stringify({ auth_code: authCode }),
    });
  },
};

// Admin endpoints
export const adminApi = {
  getUsers: async (): Promise<AdminUser[]> => {
    return apiRequest<AdminUser[]>('/api/admin/users');
  },

  broadcastOrder: async (data: BroadcastOrderRequest): Promise<BroadcastOrderResponse> => {
    return apiRequest<BroadcastOrderResponse>('/api/admin/broadcast/order', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  broadcastExit: async (positionId: number, selectedUserIds: number[]): Promise<BroadcastOrderResponse> => {
    return apiRequest<BroadcastOrderResponse>('/api/admin/broadcast/exit', {
      method: 'POST',
      body: JSON.stringify({ position_id: positionId, selected_user_ids: selectedUserIds }),
    });
  },

  getBroadcastHistory: async (): Promise<BroadcastHistoryItem[]> => {
    return apiRequest<BroadcastHistoryItem[]>('/api/admin/broadcast/history');
  },

  getBroadcastDetails: async (broadcastId: number): Promise<BroadcastOrderResponse> => {
    return apiRequest<BroadcastOrderResponse>(`/api/admin/broadcast/${broadcastId}`);
  },
};

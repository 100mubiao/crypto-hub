const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export interface ApiCoin {
  id: string
  symbol: string
  name: string
  image: string
  rank: number
  price: number
  change_24h: number
  volume: number
  market_cap: number
  turnover_rate: number
  on_chain_activity: number
  social_heat: number
  listing_time: string
  is_new: boolean
  heat_score: number
  risk_level: string
  chain: string
  holders: number
  top_holder_percent: number
  description: string
}

export interface ApiTrend {
  id: string
  coin_id: string
  coin_symbol: string
  coin_name: string
  coin_image: string
  type: string
  title: string
  score: number
  change: number
  source: string
  keywords: string[]
  timestamp: string
}

export interface ApiAlert {
  id: string
  coin_id: string
  coin_symbol: string
  coin_name: string
  type: string
  title: string
  severity: string
  description: string
  timestamp: string
}

export interface ApiOhlcPoint {
  time: number
  open: number
  high: number
  low: number
  close: number
}

export interface ApiMarketOverview {
  total_market_cap: number
  total_volume_24h: number
  btc_dominance: number
  new_coins_24h: number
  updated_at: string
}

async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { 'Accept': 'application/json' },
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return null
    return await res.json() as T
  } catch {
    return null
  }
}

export async function fetchCoins(params?: {
  symbol?: string
  chain?: string
  sort_by?: string
  limit?: number
}): Promise<ApiCoin[] | null> {
  const q = new URLSearchParams()
  if (params?.symbol) q.set('symbol', params.symbol)
  if (params?.chain) q.set('chain', params.chain)
  if (params?.sort_by) q.set('sort_by', params.sort_by)
  if (params?.limit) q.set('limit', String(params.limit))
  return fetchJson<ApiCoin[]>(`/api/v1/coins?${q.toString()}`)
}

export async function fetchCoin(id: string): Promise<ApiCoin | null> {
  return fetchJson<ApiCoin>(`/api/v1/coins/${id}`)
}

export async function fetchMarketOverview(): Promise<ApiMarketOverview | null> {
  return fetchJson<ApiMarketOverview>('/api/v1/market/overview')
}

export async function fetchNewCoins(): Promise<ApiCoin[] | null> {
  return fetchJson<ApiCoin[]>('/api/v1/new-coins')
}

export async function fetchTrends(type?: string): Promise<ApiTrend[] | null> {
  const q = type ? `?type=${type}` : ''
  return fetchJson<ApiTrend[]>(`/api/v1/trends${q}`)
}

export async function fetchAlerts(severity?: string): Promise<ApiAlert[] | null> {
  const q = severity ? `?severity=${severity}` : ''
  return fetchJson<ApiAlert[]>(`/api/v1/alerts${q}`)
}

export async function fetchChartData(coinId: string, days: number = 7): Promise<ApiOhlcPoint[] | null> {
  try {
    const url = `${API_BASE}/api/v1/coins/${coinId}/chart?days=${days}`
    const res = await fetch(url, {
      headers: { 'Accept': 'application/json' },
      signal: AbortSignal.timeout(15000),
    })
    if (!res.ok) return null
    return await res.json() as ApiOhlcPoint[]
  } catch {
    return null
  }
}

export interface LoginResponse {
  access_token: string
  token_type: string
  email: string
  name: string
  membership: string
}

export interface MeResponse {
  id: string
  email: string
  name: string
  membership: string
  membership_expiry: string | null
}

export interface PurchaseResponse {
  message: string
  membership: string
}

async function authFetch<T>(path: string, options?: RequestInit): Promise<T | null> {
  const token = localStorage.getItem('crypto_token')
  if (!token) return null
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options?.headers,
      },
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return null
    return await res.json() as T
  } catch {
    return null
  }
}

export async function apiLogin(email: string, password: string): Promise<LoginResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email, password }),
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return null
    return await res.json() as LoginResponse
  } catch {
    return null
  }
}

export async function apiRegister(email: string, name: string, password: string): Promise<LoginResponse | null> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify({ email, name, password }),
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) return null
    return await res.json() as LoginResponse
  } catch {
    return null
  }
}

export async function apiGetMe(): Promise<MeResponse | null> {
  return authFetch<MeResponse>('/api/v1/auth/me')
}

export async function apiPurchase(plan: string): Promise<PurchaseResponse | null> {
  return authFetch<PurchaseResponse>('/api/v1/auth/purchase', {
    method: 'POST',
    body: JSON.stringify({ plan }),
  })
}

export interface CheckoutSessionResponse {
  url: string
}

export interface PaymentSuccessResponse {
  membership: string
  membership_expiry: string | null
}

export async function apiCreateCheckoutSession(plan: string): Promise<CheckoutSessionResponse | null> {
  return authFetch<CheckoutSessionResponse>('/api/v1/payment/create-checkout-session', {
    method: 'POST',
    body: JSON.stringify({ plan }),
  })
}

export async function apiGetPaymentSuccess(sessionId: string): Promise<PaymentSuccessResponse | null> {
  return authFetch<PaymentSuccessResponse>(`/api/v1/payment/success?session_id=${encodeURIComponent(sessionId)}`)
}

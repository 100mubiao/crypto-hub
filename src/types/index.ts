export interface Coin {
  id: string
  rank: number
  symbol: string
  name: string
  image: string
  price: number
  change24h: number
  volume: number
  marketCap: number
  turnoverRate: number
  onChainActivity: number
  socialHeat: number
  listingTime: string
  isNew: boolean
  heatScore: number
  riskLevel: 'low' | 'medium' | 'high'
  chain: string
  holders: number
  topHolderPercent: number
  description?: string
}

export interface TrendItem {
  id: string
  coinId: string
  coinSymbol: string
  coinName: string
  coinImage: string
  type: 'heat' | 'media' | 'community' | 'event'
  title: string
  score: number
  change: number
  source?: string
  keywords?: string[]
  timestamp: string
}

export interface AlertEvent {
  id: string
  coinId: string
  coinSymbol: string
  coinName: string
  type: 'listing' | 'funding' | 'upgrade' | 'celebrity' | 'policy'
  title: string
  severity: 'low' | 'medium' | 'high'
  timestamp: string
  description?: string
}

export interface NewsCoin {
  id: string
  name: string
  symbol: string
  image: string
  listingTime: string
  initialVolume: number
  socialHeat: number
  chain: string
  isPotential: boolean
}

export interface AdvancedFilter {
  marketCapMin?: number
  marketCapMax?: number
  volumeMin?: number
  volumeMax?: number
  changeMin?: number
  changeMax?: number
  listedWithin?: string
  onChainTxMin?: number
  holdersMin?: number
  topHolderPercentMax?: number
  chains?: string[]
  search?: string
  exactMatch?: boolean
}

export interface SavedStrategy {
  id: string
  name: string
  filters: AdvancedFilter
  alerts: boolean
  createdAt: string
}

export interface UserInfo {
  email: string
  name: string
  membership: 'free' | 'premium' | 'lifetime'
}

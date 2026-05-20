import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { mockCoins, mockTrends, mockAlerts, mockNewCoins } from '@/data/mock'
import type { Coin, TrendItem, AlertEvent, NewsCoin, SavedStrategy, UserInfo } from '@/types'
import {
  fetchCoins as apiFetchCoins,
  fetchNewCoins as apiFetchNewCoins,
  fetchTrends as apiFetchTrends,
  fetchAlerts as apiFetchAlerts,
  apiLogin,
  apiRegister,
  apiPurchase,
  apiGetMe,
  type ApiCoin,
  type ApiTrend,
  type ApiAlert,
} from '@/api'

function mapApiCoin(c: ApiCoin): Coin {
  return {
    id: c.id,
    rank: c.rank,
    symbol: c.symbol,
    name: c.name,
    image: c.image,
    price: c.price,
    change24h: c.change_24h,
    volume: c.volume,
    marketCap: c.market_cap,
    turnoverRate: c.turnover_rate,
    onChainActivity: c.on_chain_activity,
    socialHeat: c.social_heat,
    listingTime: c.listing_time,
    isNew: c.is_new,
    heatScore: c.heat_score,
    riskLevel: c.risk_level as Coin['riskLevel'],
    chain: c.chain,
    holders: c.holders,
    topHolderPercent: c.top_holder_percent,
  }
}

function mapApiTrend(t: ApiTrend): TrendItem {
  return {
    id: t.id,
    coinId: t.coin_id,
    coinSymbol: t.coin_symbol,
    coinName: t.coin_name,
    coinImage: t.coin_image,
    type: t.type as TrendItem['type'],
    title: t.title,
    score: t.score,
    change: t.change,
    source: t.source,
    keywords: t.keywords,
    timestamp: t.timestamp,
  }
}

function mapApiAlert(a: ApiAlert): AlertEvent {
  return {
    id: a.id,
    coinId: a.coin_id,
    coinSymbol: a.coin_symbol,
    coinName: a.coin_name,
    type: a.type as AlertEvent['type'],
    title: a.title,
    severity: a.severity as AlertEvent['severity'],
    description: a.description,
    timestamp: a.timestamp,
  }
}

export const useCryptoStore = defineStore('crypto', () => {
  const coins = ref<Coin[]>([])
  const trends = ref<TrendItem[]>([])
  const alerts = ref<AlertEvent[]>([])
  const newCoins = ref<NewsCoin[]>([])
  const savedStrategies = ref<SavedStrategy[]>([])
  const isMember = ref(false)
  const user = ref<UserInfo | null>(null)
  const token = ref(localStorage.getItem('crypto_token') || '')
  const searchQuery = ref('')
  const selectedChain = ref<string>('all')
  const loading = ref(false)
  const error = ref<string | null>(null)
  const usingMock = ref(true)
  const theme = ref(localStorage.getItem('crypto_theme') || 'default')

  function setTheme(t: string) {
    theme.value = t
    localStorage.setItem('crypto_theme', t)
    document.documentElement.classList.toggle('theme-neon', t === 'neon')
    document.documentElement.classList.toggle('theme-transition', true)
    setTimeout(() => document.documentElement.classList.remove('theme-transition'), 400)
  }

  const hotCoins = computed(() =>
    [...coins.value].sort((a, b) => b.heatScore - a.heatScore).slice(0, 5)
  )

  const gainers = computed(() =>
    [...coins.value].filter(c => c.change24h > 10).sort((a, b) => b.change24h - a.change24h)
  )

  const losers = computed(() =>
    [...coins.value].filter(c => c.change24h < -10).sort((a, b) => a.change24h - b.change24h)
  )

  const volumeSpikers = computed(() =>
    [...coins.value].filter(c => c.turnoverRate > 30).sort((a, b) => b.turnoverRate - a.turnoverRate)
  )

  const todayNew = computed(() => {
    const dayAgo = Date.now() - 24 * 60 * 60 * 1000
    return coins.value.filter(c => new Date(c.listingTime).getTime() > dayAgo)
  })

  const filteredCoins = computed(() => {
    let result = coins.value
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      result = result.filter(c =>
        c.name.toLowerCase().includes(q) || c.symbol.toLowerCase().includes(q)
      )
    }
    if (selectedChain.value !== 'all') {
      result = result.filter(c => c.chain === selectedChain.value)
    }
    return result
  })

  async function initialize() {
    loading.value = true
    error.value = null
    await restoreSession()

    const [coinData, newCoinData, trendData, alertData] = await Promise.all([
      apiFetchCoins({ limit: 50 }),
      apiFetchNewCoins(),
      apiFetchTrends(),
      apiFetchAlerts(),
    ])

    if (coinData && coinData.length > 0) {
      coins.value = coinData.map(mapApiCoin)
      usingMock.value = false
    } else {
      coins.value = mockCoins
      usingMock.value = true
    }

    if (newCoinData && newCoinData.length > 0) {
      newCoins.value = newCoinData.map(c => ({
        id: c.id,
        name: c.name,
        symbol: c.symbol,
        image: c.image,
        listingTime: c.listing_time,
        initialVolume: c.volume,
        socialHeat: c.social_heat,
        chain: c.chain,
        isPotential: c.heat_score > 7,
      }))
    } else {
      newCoins.value = mockNewCoins
    }

    if (trendData && trendData.length > 0) {
      trends.value = trendData.map(mapApiTrend)
    } else {
      trends.value = mockTrends
    }

    if (alertData && alertData.length > 0) {
      alerts.value = alertData.map(mapApiAlert)
    } else {
      alerts.value = mockAlerts
    }

    loading.value = false
  }

  function setMember(v: boolean) {
    isMember.value = v
  }

  async function login(email: string, password: string) {
    const res = await apiLogin(email, password)
    if (!res) throw new Error('Login failed')
    token.value = res.access_token
    localStorage.setItem('crypto_token', res.access_token)
    user.value = { email: res.email, name: res.name, membership: res.membership as UserInfo['membership'] }
    isMember.value = res.membership === 'premium' || res.membership === 'lifetime'
    return res
  }

  async function register(email: string, name: string, password: string) {
    const res = await apiRegister(email, name, password)
    if (!res) throw new Error('Registration failed')
    token.value = res.access_token
    localStorage.setItem('crypto_token', res.access_token)
    user.value = { email: res.email, name: res.name, membership: res.membership as UserInfo['membership'] }
    isMember.value = false
    return res
  }

  function logout() {
    token.value = ''
    localStorage.removeItem('crypto_token')
    user.value = null
    isMember.value = false
  }

  async function purchase(plan: string) {
    const res = await apiPurchase(plan)
    if (!res) throw new Error('Purchase failed')
    if (user.value) {
      user.value.membership = res.membership as UserInfo['membership']
      isMember.value = res.membership === 'premium' || res.membership === 'lifetime'
    }
    return res
  }

  function applyTheme(t: string) {
    document.documentElement.classList.toggle('theme-neon', t === 'neon')
    document.documentElement.classList.add('theme-transition')
    setTimeout(() => document.documentElement.classList.remove('theme-transition'), 400)
  }

  async function restoreSession() {
    if (!token.value) return
    const me = await apiGetMe()
    if (me) {
      user.value = { email: me.email, name: me.name, membership: me.membership as UserInfo['membership'] }
      isMember.value = me.membership === 'premium' || me.membership === 'lifetime'
    } else {
      token.value = ''
      localStorage.removeItem('crypto_token')
    }
  }

  applyTheme(theme.value)

  function saveStrategy(s: SavedStrategy) {
    savedStrategies.value.push(s)
  }

  function deleteStrategy(id: string) {
    savedStrategies.value = savedStrategies.value.filter(s => s.id !== id)
  }

  function getCoinById(id: string): Coin | undefined {
    return coins.value.find(c => c.id === id)
  }

  return {
    coins, trends, alerts, newCoins, savedStrategies,
    isMember, user, token, searchQuery, selectedChain,
    loading, error, usingMock, theme,
    hotCoins, gainers, losers, volumeSpikers, todayNew, filteredCoins,
    initialize, setMember, login, register, logout, purchase, restoreSession, saveStrategy, deleteStrategy, getCoinById,
    setTheme,
  }
})

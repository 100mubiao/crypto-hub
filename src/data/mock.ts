import type { Coin, TrendItem, AlertEvent, NewsCoin } from '@/types'

export const mockCoins: Coin[] = [
  { id: 'bitcoin', rank: 1, symbol: 'BTC', name: 'Bitcoin', image: 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', price: 67234.5, change24h: 2.34, volume: 28500000000, marketCap: 1320000000000, turnoverRate: 2.1, onChainActivity: 856000, socialHeat: 95, listingTime: '2010-07-17T00:00:00Z', isNew: false, heatScore: 9.2, riskLevel: 'low', chain: 'Bitcoin', holders: 52000000, topHolderPercent: 5.2 },
  { id: 'ethereum', rank: 2, symbol: 'ETH', name: 'Ethereum', image: 'https://cryptologos.cc/logos/ethereum-eth-logo.png', price: 3456.78, change24h: 5.67, volume: 18200000000, marketCap: 415000000000, turnoverRate: 4.3, onChainActivity: 1200000, socialHeat: 92, listingTime: '2015-07-30T00:00:00Z', isNew: false, heatScore: 8.8, riskLevel: 'low', chain: 'Ethereum', holders: 28000000, topHolderPercent: 8.1 },
  { id: 'solana', rank: 3, symbol: 'SOL', name: 'Solana', image: 'https://cryptologos.cc/logos/solana-sol-logo.png', price: 178.23, change24h: -1.23, volume: 5200000000, marketCap: 78000000000, turnoverRate: 6.7, onChainActivity: 2500000, socialHeat: 88, listingTime: '2020-03-16T00:00:00Z', isNew: false, heatScore: 8.5, riskLevel: 'low', chain: 'Solana', holders: 8500000, topHolderPercent: 12.3 },
  { id: 'pepe', rank: 42, symbol: 'PEPE', name: 'Pepe', image: 'https://cryptologos.cc/logos/pepe-pepe-logo.png', price: 0.00001234, change24h: 45.67, volume: 1800000000, marketCap: 5200000000, turnoverRate: 34.5, onChainActivity: 420000, socialHeat: 85, listingTime: '2024-11-01T00:00:00Z', isNew: true, heatScore: 9.5, riskLevel: 'high', chain: 'Ethereum', holders: 210000, topHolderPercent: 25.4 },
  { id: 'dogwifhat', rank: 55, symbol: 'WIF', name: 'dogwifhat', image: 'https://cryptologos.cc/logos/dogwifhat-wif-logo.png', price: 2.45, change24h: -8.92, volume: 890000000, marketCap: 2450000000, turnoverRate: 36.2, onChainActivity: 180000, socialHeat: 78, listingTime: '2024-08-15T00:00:00Z', isNew: false, heatScore: 7.8, riskLevel: 'high', chain: 'Solana', holders: 98000, topHolderPercent: 32.1 },
  { id: 'bonk', rank: 68, symbol: 'BONK', name: 'Bonk', image: 'https://cryptologos.cc/logos/bonk-bonk-logo.png', price: 0.00002345, change24h: 12.34, volume: 650000000, marketCap: 1500000000, turnoverRate: 43.3, onChainActivity: 320000, socialHeat: 72, listingTime: '2024-06-20T00:00:00Z', isNew: false, heatScore: 7.2, riskLevel: 'high', chain: 'Solana', holders: 156000, topHolderPercent: 28.7 },
  { id: 'avalanche', rank: 12, symbol: 'AVAX', name: 'Avalanche', image: 'https://cryptologos.cc/logos/avalanche-avax-logo.png', price: 38.92, change24h: 3.45, volume: 980000000, marketCap: 15200000000, turnoverRate: 6.4, onChainActivity: 89000, socialHeat: 65, listingTime: '2020-09-22T00:00:00Z', isNew: false, heatScore: 6.5, riskLevel: 'medium', chain: 'Avalanche', holders: 1200000, topHolderPercent: 15.8 },
  { id: 'chainlink', rank: 15, symbol: 'LINK', name: 'Chainlink', image: 'https://cryptologos.cc/logos/chainlink-link-logo.png', price: 18.45, change24h: -2.15, volume: 780000000, marketCap: 10800000000, turnoverRate: 7.2, onChainActivity: 45000, socialHeat: 62, listingTime: '2017-09-21T00:00:00Z', isNew: false, heatScore: 6.2, riskLevel: 'low', chain: 'Ethereum', holders: 750000, topHolderPercent: 18.2 },
  { id: 'newcoin-abc', rank: 245, symbol: 'NABC', name: 'NewCoin ABC', image: '', price: 0.00123, change24h: 156.78, volume: 45000000, marketCap: 12000000, turnoverRate: 375, onChainActivity: 25000, socialHeat: 55, listingTime: '2026-05-07T08:00:00Z', isNew: true, heatScore: 8.1, riskLevel: 'high', chain: 'Base', holders: 3400, topHolderPercent: 45.2 },
  { id: 'newcoin-xyz', rank: 312, symbol: 'XYZ', name: 'XYZ Token', image: '', price: 0.000567, change24h: 89.12, volume: 21000000, marketCap: 5600000, turnoverRate: 375, onChainActivity: 12000, socialHeat: 48, listingTime: '2026-05-07T12:30:00Z', isNew: true, heatScore: 7.5, riskLevel: 'high', chain: 'Solana', holders: 1800, topHolderPercent: 52.3 },
  { id: 'nova', rank: 178, symbol: 'NOVA', name: 'Nova Finance', image: '', price: 0.0456, change24h: 234.5, volume: 89000000, marketCap: 45000000, turnoverRate: 197.8, onChainActivity: 68000, socialHeat: 60, listingTime: '2026-05-06T00:00:00Z', isNew: true, heatScore: 9.0, riskLevel: 'high', chain: 'Ethereum', holders: 8900, topHolderPercent: 38.5 },
  { id: 'mooncoin', rank: 156, symbol: 'MOON', name: 'MoonCoin', image: '', price: 0.0891, change24h: -34.56, volume: 156000000, marketCap: 89000000, turnoverRate: 175.3, onChainActivity: 95000, socialHeat: 68, listingTime: '2026-04-20T00:00:00Z', isNew: false, heatScore: 6.8, riskLevel: 'high', chain: 'BSC', holders: 15000, topHolderPercent: 30.1 },
  { id: 'defi-swap', rank: 89, symbol: 'DSWP', name: 'DeFi Swap', image: '', price: 0.5678, change24h: -12.34, volume: 234000000, marketCap: 340000000, turnoverRate: 68.8, onChainActivity: 120000, socialHeat: 58, listingTime: '2025-12-01T00:00:00Z', isNew: false, heatScore: 5.5, riskLevel: 'medium', chain: 'Arbitrum', holders: 45000, topHolderPercent: 22.4 },
  { id: 'ai-token', rank: 134, symbol: 'AIT', name: 'AI Token', image: '', price: 0.2345, change24h: 67.89, volume: 345000000, marketCap: 234000000, turnoverRate: 147.4, onChainActivity: 210000, socialHeat: 82, listingTime: '2026-03-15T00:00:00Z', isNew: false, heatScore: 8.3, riskLevel: 'medium', chain: 'Solana', holders: 32000, topHolderPercent: 20.5 },
]

export const mockTrends: TrendItem[] = [
  { id: 't1', coinId: 'pepe', coinSymbol: 'PEPE', coinName: 'Pepe', coinImage: '', type: 'heat', title: 'PEPE surges 45% amid meme coin rally', score: 9.5, change: 5.2, source: 'Twitter/X', timestamp: '2026-05-08T00:30:00Z' },
  { id: 't2', coinId: 'nova', coinSymbol: 'NOVA', coinName: 'Nova Finance', coinImage: '', type: 'heat', title: 'NOVA launches mainnet, TVL surges', score: 9.0, change: 8.7, source: 'Twitter/X', timestamp: '2026-05-07T23:00:00Z' },
  { id: 't3', coinId: 'bitcoin', coinSymbol: 'BTC', coinName: 'Bitcoin', coinImage: '', type: 'heat', title: 'BTC holds $67K as ETF inflows continue', score: 8.5, change: -1.2, source: 'Bloomberg', timestamp: '2026-05-08T01:00:00Z' },
  { id: 't4', coinId: 'ai-token', coinSymbol: 'AIT', coinName: 'AI Token', coinImage: '', type: 'heat', title: 'AI Token partnership with major GPU provider', score: 8.3, change: 12.1, source: 'Twitter/X', timestamp: '2026-05-07T22:00:00Z' },
  { id: 't5', coinId: 'solana', coinSymbol: 'SOL', coinName: 'Solana', coinImage: '', type: 'media', title: 'Analysts predict Solana ecosystem growth in Q3', score: 7.8, change: 3.4, source: 'CoinDesk', timestamp: '2026-05-08T00:00:00Z' },
  { id: 't6', coinId: 'bonk', coinSymbol: 'BONK', coinName: 'Bonk', coinImage: '', type: 'community', title: 'Bonk community votes on burn proposal', score: 7.2, change: 6.5, source: 'Discord', keywords: ['burn', 'voting', 'supply'], timestamp: '2026-05-07T20:00:00Z' },
  { id: 't7', coinId: 'newcoin-abc', coinSymbol: 'NABC', coinName: 'NewCoin ABC', coinImage: '', type: 'event', title: 'NABC listed on KuCoin', score: 8.1, change: 0, source: 'KuCoin Announcement', timestamp: '2026-05-07T14:00:00Z' },
  { id: 't8', coinId: 'mooncoin', coinSymbol: 'MOON', coinName: 'MoonCoin', coinImage: '', type: 'media', title: 'MoonCoin rug pull concerns after dev wallet moves', score: 6.8, change: -15.3, source: 'Cointelegraph', timestamp: '2026-05-07T18:00:00Z' },
]

export const mockAlerts: AlertEvent[] = [
  { id: 'a1', coinId: 'newcoin-abc', coinSymbol: 'NABC', coinName: 'NewCoin ABC', type: 'listing', title: 'NABC listed on KuCoin and Gate.io', severity: 'high', timestamp: '2026-05-07T14:00:00Z', description: 'New token NABC has been listed on 2 major exchanges within 6 hours of launch.' },
  { id: 'a2', coinId: 'ai-token', coinSymbol: 'AIT', coinName: 'AI Token', type: 'funding', title: 'AI Token raises $50M Series B', severity: 'high', timestamp: '2026-05-07T16:00:00Z', description: 'AI Token secured $50M in Series B funding led by a16z.' },
  { id: 'a3', coinId: 'nova', coinSymbol: 'NOVA', coinName: 'Nova Finance', type: 'upgrade', title: 'Nova Finance Mainnet Launches Successfully', severity: 'medium', timestamp: '2026-05-07T12:00:00Z', description: 'Nova Finance mainnet went live with initial TVL of $200M.' },
  { id: 'a4', coinId: 'pepe', coinSymbol: 'PEPE', coinName: 'Pepe', type: 'celebrity', title: 'Elon Musk tweets Pepe meme', severity: 'high', timestamp: '2026-05-07T22:30:00Z', description: 'Elon Musk posted a Pepe-themed meme causing price surge.' },
]

export const mockNewCoins: NewsCoin[] = [
  { id: 'newcoin-abc', name: 'NewCoin ABC', symbol: 'NABC', image: '', listingTime: '2026-05-07T08:00:00Z', initialVolume: 45000000, socialHeat: 55, chain: 'Base', isPotential: true },
  { id: 'newcoin-xyz', name: 'XYZ Token', symbol: 'XYZ', image: '', listingTime: '2026-05-07T12:30:00Z', initialVolume: 21000000, socialHeat: 48, chain: 'Solana', isPotential: false },
  { id: 'speedcoin', name: 'Speed Coin', symbol: 'SPD', image: '', listingTime: '2026-05-07T18:00:00Z', initialVolume: 5800000, socialHeat: 35, chain: 'BSC', isPotential: false },
  { id: 'zenith', name: 'Zenith Protocol', symbol: 'ZNT', image: '', listingTime: '2026-05-07T22:00:00Z', initialVolume: 12000000, socialHeat: 42, chain: 'Ethereum', isPotential: true },
]

export function formatPrice(p: number): string {
  if (p >= 1) return '$' + p.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  if (p >= 0.0001) return '$' + p.toFixed(6)
  return '$' + p.toFixed(8)
}

export function formatVolume(v: number): string {
  if (v >= 1_000_000_000) return '$' + (v / 1_000_000_000).toFixed(2) + 'B'
  if (v >= 1_000_000) return '$' + (v / 1_000_000).toFixed(2) + 'M'
  if (v >= 1_000) return '$' + (v / 1_000).toFixed(2) + 'K'
  return '$' + v.toFixed(2)
}

export function formatMarketCap(v: number): string {
  if (v >= 1_000_000_000_000) return '$' + (v / 1_000_000_000_000).toFixed(2) + 'T'
  if (v >= 1_000_000_000) return '$' + (v / 1_000_000_000).toFixed(2) + 'B'
  if (v >= 1_000_000) return '$' + (v / 1_000_000).toFixed(2) + 'M'
  return '$' + v.toLocaleString('en-US')
}

export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return mins + 'm ago'
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return hrs + 'h ago'
  const days = Math.floor(hrs / 24)
  return days + 'd ago'
}

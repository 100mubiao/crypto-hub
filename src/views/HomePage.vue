<script setup lang="ts">
import { useCryptoStore } from '@/stores/crypto'
import { formatPrice, formatVolume, formatMarketCap, timeAgo } from '@/data/mock'
import StatCard from '@/components/StatCard.vue'
import HeatScore from '@/components/HeatScore.vue'
import RiskBadge from '@/components/RiskBadge.vue'
import AdSlot from '@/components/AdSlot.vue'

const store = useCryptoStore()

function changeClass(v: number) {
  return v >= 0 ? 'positive' : 'negative'
}

function changeSign(v: number) {
  return v >= 0 ? '+' : ''
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
    <!-- Hero -->
    <div class="text-center mb-8">
      <h1 class="text-3xl sm:text-4xl font-bold text-white">Crypto Market Dashboard</h1>
      <p class="text-crypto-400 mt-2 text-sm sm:text-base">
        Real-time data aggregation &middot; New coin radar &middot; Smart filtering
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="store.loading && store.coins.length === 0" class="flex flex-col items-center justify-center py-20">
      <div class="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin mb-4"></div>
      <p class="text-crypto-400 text-sm">Fetching live data from CoinGecko...</p>
      <p class="text-crypto-500 text-xs mt-1">Using demo data if backend is unavailable</p>
    </div>

    <!-- Stats row -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
      <StatCard title="Total Market Cap" :value="formatMarketCap(1320000000000 + 415000000000 + 78000000000)" change="+2.1%" trend="up" icon="📊" />
      <StatCard title="24h Volume" :value="formatVolume(28500000000 + 18200000000 + 5200000000)" change="+12.4%" trend="up" icon="💰" />
      <StatCard title="BTC Dominance" value="58.3%" change="-0.8%" trend="down" icon="₿" />
      <StatCard title="New Coins (24h)" :value="String(store.todayNew.length)" change="+3" trend="up" icon="🆕" />
    </div>

    <!-- Search & Filter -->
    <div class="card mb-6">
      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-crypto-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input
            v-model="store.searchQuery"
            type="text"
            placeholder="Search by name or symbol..."
            class="w-full bg-crypto-700 border border-crypto-600 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-crypto-400 focus:outline-none focus:border-accent transition-colors"
          />
        </div>
        <select
          v-model="store.selectedChain"
          class="bg-crypto-700 border border-crypto-600 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-accent"
        >
          <option value="all">All Chains</option>
          <option value="Bitcoin">Bitcoin</option>
          <option value="Ethereum">Ethereum</option>
          <option value="Solana">Solana</option>
          <option value="BSC">BSC</option>
          <option value="Base">Base</option>
          <option value="Arbitrum">Arbitrum</option>
          <option value="Polygon">Polygon</option>
          <option value="Avalanche">Avalanche</option>
        </select>
      </div>
    </div>

    <!-- Ad Banner -->
    <AdSlot type="banner" class="mb-6" />

    <!-- Coin Table -->
    <div class="card overflow-x-auto mb-8">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold text-white">All Coins</h2>
        <span class="text-xs text-crypto-400">{{ store.filteredCoins.length }} coins</span>
      </div>
      <table class="table-base">
        <thead>
          <tr>
            <th>#</th>
            <th>Name</th>
            <th>Price</th>
            <th>24h Change</th>
            <th>Volume</th>
            <th>Market Cap</th>
            <th>Heat</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="coin in store.filteredCoins" :key="coin.id" class="cursor-pointer" @click="$router.push('/coin/' + coin.id)">
            <td class="text-crypto-400 text-xs">{{ coin.rank }}</td>
            <td>
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-crypto-600 flex items-center justify-center text-[8px] overflow-hidden">
                  <img v-if="coin.image" :src="coin.image" :alt="coin.symbol" class="w-full h-full object-cover" />
                  <span v-else class="text-crypto-300 font-bold">{{ coin.symbol.slice(0, 2) }}</span>
                </div>
                <div>
                  <span class="font-medium text-white">{{ coin.symbol }}</span>
                  <span v-if="coin.isNew" class="ml-1.5 text-[10px] bg-accent/20 text-accent px-1 rounded">NEW</span>
                </div>
              </div>
            </td>
            <td class="font-mono text-white">{{ formatPrice(coin.price) }}</td>
            <td :class="changeClass(coin.change24h)" class="font-mono">
              {{ changeSign(coin.change24h) }}{{ coin.change24h.toFixed(2) }}%
            </td>
            <td class="font-mono text-crypto-300">{{ formatVolume(coin.volume) }}</td>
            <td class="font-mono text-crypto-300">{{ formatMarketCap(coin.marketCap) }}</td>
            <td><HeatScore :score="coin.heatScore" size="sm" /></td>
            <td><RiskBadge :level="coin.riskLevel" /></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Quick Sections Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Today's New Coins -->
      <div class="card">
        <h3 class="text-white font-bold mb-4 flex items-center gap-2">
          <span class="text-lg">🆕</span> Today's New Coins
        </h3>
        <div v-if="store.todayNew.length === 0" class="text-crypto-400 text-sm py-4 text-center">No new coins in the last 24h</div>
        <div v-for="coin in store.todayNew" :key="coin.id" class="flex items-center justify-between py-2.5 border-b border-crypto-700 last:border-0 cursor-pointer" @click="$router.push('/coin/' + coin.id)">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full bg-crypto-700 flex items-center justify-center text-[10px] font-bold text-crypto-300">{{ coin.symbol.slice(0, 2) }}</div>
            <div>
              <span class="text-sm font-medium text-white">{{ coin.symbol }}</span>
              <span class="text-xs text-crypto-500 ml-2">{{ coin.chain }}</span>
            </div>
          </div>
          <div class="text-right">
            <div class="text-sm font-mono text-white">{{ formatPrice(coin.price) }}</div>
            <div :class="changeClass(coin.change24h)" class="text-xs font-mono">{{ changeSign(coin.change24h) }}{{ coin.change24h.toFixed(2) }}%</div>
          </div>
        </div>
      </div>

      <!-- 24h Gainers -->
      <div class="card">
        <h3 class="text-white font-bold mb-4 flex items-center gap-2">
          <span class="text-lg">🚀</span> 24h Top Gainers
        </h3>
        <div v-for="coin in store.gainers.slice(0, 5)" :key="coin.id" class="flex items-center justify-between py-2.5 border-b border-crypto-700 last:border-0 cursor-pointer" @click="$router.push('/coin/' + coin.id)">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full bg-crypto-700 flex items-center justify-center text-[10px] font-bold text-crypto-300">{{ coin.symbol.slice(0, 2) }}</div>
            <span class="text-sm font-medium text-white">{{ coin.symbol }}</span>
          </div>
          <div class="text-right">
            <div class="text-sm font-mono text-white">{{ formatPrice(coin.price) }}</div>
            <div class="text-xs font-mono positive">{{ changeSign(coin.change24h) }}{{ coin.change24h.toFixed(2) }}%</div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Volume Spikers -->
      <div class="card">
        <h3 class="text-white font-bold mb-4 flex items-center gap-2">
          <span class="text-lg">📈</span> Volume Spikers
        </h3>
        <div v-if="store.volumeSpikers.length === 0" class="text-crypto-400 text-sm py-4 text-center">None at this time</div>
        <div v-for="coin in store.volumeSpikers.slice(0, 5)" :key="coin.id" class="flex items-center justify-between py-2.5 border-b border-crypto-700 last:border-0 cursor-pointer" @click="$router.push('/coin/' + coin.id)">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full bg-crypto-700 flex items-center justify-center text-[10px] font-bold text-crypto-300">{{ coin.symbol.slice(0, 2) }}</div>
            <span class="text-sm font-medium text-white">{{ coin.symbol }}</span>
          </div>
          <div class="text-right">
            <div class="text-sm font-mono text-white">{{ formatVolume(coin.volume) }}</div>
            <div class="text-xs font-mono text-hot">{{ coin.turnoverRate.toFixed(1) }}% turnover</div>
          </div>
        </div>
      </div>

      <!-- Hot Events -->
      <div class="card">
        <h3 class="text-white font-bold mb-4 flex items-center gap-2">
          <span class="text-lg">⚡</span> Latest Events
        </h3>
        <div v-for="evt in store.alerts.slice(0, 4)" :key="evt.id" class="py-2.5 border-b border-crypto-700 last:border-0">
          <div class="flex items-start gap-2">
            <span
              class="mt-0.5 text-[10px] px-1.5 py-0.5 rounded font-medium"
              :class="evt.severity === 'high' ? 'bg-hot/20 text-hot' : evt.severity === 'medium' ? 'bg-warn/20 text-warn' : 'bg-accent/20 text-accent'"
            >
              {{ evt.severity }}
            </span>
            <div class="flex-1 min-w-0">
              <p class="text-sm text-white cursor-pointer hover:text-accent transition-colors" @click="$router.push('/coin/' + evt.coinId)">{{ evt.title }}</p>
              <p class="text-xs text-crypto-500 mt-0.5">{{ timeAgo(evt.timestamp) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Ad -->
    <AdSlot type="banner" class="mb-4" />
  </div>
</template>

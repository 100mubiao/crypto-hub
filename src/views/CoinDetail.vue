<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'
import { formatPrice, formatVolume, formatMarketCap } from '@/data/mock'
import HeatScore from '@/components/HeatScore.vue'
import RiskBadge from '@/components/RiskBadge.vue'
import AdSlot from '@/components/AdSlot.vue'
import MemberGate from '@/components/MemberGate.vue'
import PriceChart from '@/components/PriceChart.vue'
import { fetchChartData } from '@/api'

const route = useRoute()
const router = useRouter()
const store = useCryptoStore()

const coin = computed(() => store.getCoinById(route.params.id as string))

onMounted(() => {
  if (store.coins.length === 0) {
    store.initialize()
  }
})

function changeClass(v: number) {
  return v >= 0 ? 'positive' : 'negative'
}
function changeSign(v: number) {
  return v >= 0 ? '+' : ''
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
    <div v-if="!coin && store.loading" class="flex flex-col items-center justify-center py-20">
      <div class="w-10 h-10 border-2 border-accent border-t-transparent rounded-full animate-spin mb-4"></div>
      <p class="text-crypto-400 text-sm">Loading coin data...</p>
    </div>
    <div v-else-if="!coin" class="text-center py-20">
      <p class="text-crypto-400">Coin not found</p>
      <button @click="router.push('/')" class="btn-primary mt-4">Back to Dashboard</button>
    </div>

    <template v-else>
      <!-- Back + Header -->
      <button @click="router.push('/')" class="text-crypto-400 hover:text-white text-sm mb-4 flex items-center gap-1 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
        Back to Dashboard
      </button>

      <div class="card mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-crypto-700 flex items-center justify-center text-sm font-bold text-crypto-300 overflow-hidden">
              <img v-if="coin.image" :src="coin.image" :alt="coin.symbol" class="w-full h-full object-cover" />
              <span v-else>{{ coin.symbol.slice(0, 2) }}</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <h1 class="text-2xl font-bold text-white">{{ coin.name }}</h1>
                <span class="text-crypto-400 text-sm">{{ coin.symbol }}</span>
                <span v-if="coin.isNew" class="text-[10px] bg-accent/20 text-accent px-1.5 py-0.5 rounded">NEW</span>
              </div>
              <div class="flex items-center gap-3 mt-1">
                <span class="text-xs text-crypto-500">Rank #{{ coin.rank }}</span>
                <RiskBadge :level="coin.riskLevel" />
              </div>
            </div>
          </div>
          <div class="sm:ml-auto text-right">
            <div class="text-3xl font-bold text-white font-mono">{{ formatPrice(coin.price) }}</div>
            <div :class="changeClass(coin.change24h)" class="font-mono text-sm">
              {{ changeSign(coin.change24h) }}{{ coin.change24h.toFixed(2) }}% (24h)
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main Column -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Risk Warning -->
          <div class="bg-hot/10 border border-hot/20 rounded-lg p-4">
            <p class="text-xs text-hot font-medium">
              ⚠️ RISK DISCLAIMER: Cryptocurrency trading involves substantial risk. This data is for informational purposes only.
              {{ coin.riskLevel === 'high' ? 'This coin carries HIGH risk due to volatility and market cap.' : '' }}
              Never invest more than you can afford to lose.
            </p>
          </div>

          <!-- Key Metrics -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div class="card text-center">
              <p class="text-crypto-400 text-xs">Market Cap</p>
              <p class="text-white font-bold font-mono text-sm mt-1">{{ formatMarketCap(coin.marketCap) }}</p>
            </div>
            <div class="card text-center">
              <p class="text-crypto-400 text-xs">24h Volume</p>
              <p class="text-white font-bold font-mono text-sm mt-1">{{ formatVolume(coin.volume) }}</p>
            </div>
            <div class="card text-center">
              <p class="text-crypto-400 text-xs">Turnover Rate</p>
              <p class="text-white font-bold font-mono text-sm mt-1">{{ coin.turnoverRate.toFixed(1) }}%</p>
            </div>
            <div class="card text-center">
              <p class="text-crypto-400 text-xs">On-Chain Activity</p>
              <p class="text-white font-bold font-mono text-sm mt-1">{{ (coin.onChainActivity / 1000).toFixed(0) }}K</p>
            </div>
          </div>

          <!-- Price Chart (Premium only) -->
          <MemberGate>
            <PriceChart
              :coin-id="coin.id"
              :fetch-fn="fetchChartData"
            />
          </MemberGate>

          <!-- On-chain Data -->
          <div class="card">
            <h3 class="text-white font-bold mb-3">On-Chain Data</h3>
            <div class="grid grid-cols-3 gap-4">
              <div>
                <p class="text-crypto-400 text-xs">Holders</p>
                <p class="text-white font-bold font-mono text-sm">{{ (coin.holders / 1000).toFixed(0) }}K</p>
              </div>
              <div>
                <p class="text-crypto-400 text-xs">Top 10% Holders</p>
                <p class="text-white font-bold font-mono text-sm">{{ coin.topHolderPercent.toFixed(1) }}%</p>
              </div>
              <div>
                <p class="text-crypto-400 text-xs">Chain</p>
                <p class="text-white font-bold font-mono text-sm">{{ coin.chain }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Heat Score -->
          <div class="card">
            <h3 class="text-white font-bold mb-3">Heat Score</h3>
            <HeatScore :score="coin.heatScore" />
            <p class="text-crypto-400 text-xs mt-2">Based on social activity, media mentions, and community discussion</p>
          </div>

          <!-- Exchange Links -->
          <div class="card">
            <h3 class="text-white font-bold mb-3">Trade on</h3>
            <div class="space-y-2">
              <a href="#" class="block bg-crypto-700 hover:bg-crypto-600 rounded-lg px-3 py-2 text-sm text-white transition-colors">Binance</a>
              <a href="#" class="block bg-crypto-700 hover:bg-crypto-600 rounded-lg px-3 py-2 text-sm text-white transition-colors">Coinbase</a>
              <a href="#" class="block bg-crypto-700 hover:bg-crypto-600 rounded-lg px-3 py-2 text-sm text-white transition-colors">Uniswap</a>
              <a href="#" class="block bg-crypto-700 hover:bg-crypto-600 rounded-lg px-3 py-2 text-sm text-crypto-400 transition-colors">View all &rarr;</a>
            </div>
          </div>

          <!-- Social Heat -->
          <div class="card">
            <h3 class="text-white font-bold mb-3">Social Heat</h3>
            <div class="flex items-center gap-2">
              <span class="text-xs text-crypto-400">Twitter/X</span>
              <span class="text-sm font-bold text-white">{{ coin.socialHeat }}/100</span>
            </div>
          </div>

          <!-- Ad Sidebar -->
          <AdSlot type="sidebar" />
        </div>
      </div>

      <!-- Bottom Ad -->
      <AdSlot type="native" class="mt-6" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCryptoStore } from '@/stores/crypto'
import { formatPrice, formatVolume, formatMarketCap } from '@/data/mock'
import MemberGate from '@/components/MemberGate.vue'
import HeatScore from '@/components/HeatScore.vue'
import RiskBadge from '@/components/RiskBadge.vue'
import type { AdvancedFilter as FilterType } from '@/types'

const store = useCryptoStore()

const filters = ref<FilterType>({
  changeMin: undefined,
  changeMax: undefined,
  volumeMin: undefined,
  volumeMax: undefined,
  marketCapMin: undefined,
  marketCapMax: undefined,
  chains: [],
})

const chainOptions = ['Ethereum', 'Solana', 'BSC', 'Base', 'Arbitrum', 'Polygon', 'Avalanche']

function toggleChain(chain: string) {
  if (!filters.value.chains) filters.value.chains = []
  const idx = filters.value.chains.indexOf(chain)
  if (idx >= 0) filters.value.chains.splice(idx, 1)
  else filters.value.chains.push(chain)
}

const results = computed(() => {
  return store.coins.filter(c => {
    if (filters.value.changeMin !== undefined && c.change24h < filters.value.changeMin) return false
    if (filters.value.changeMax !== undefined && c.change24h > filters.value.changeMax) return false
    if (filters.value.volumeMin !== undefined && c.volume < filters.value.volumeMin) return false
    if (filters.value.volumeMax !== undefined && c.volume > filters.value.volumeMax) return false
    if (filters.value.marketCapMin !== undefined && c.marketCap < filters.value.marketCapMin) return false
    if (filters.value.marketCapMax !== undefined && c.marketCap > filters.value.marketCapMax) return false
    if (filters.value.chains && filters.value.chains.length > 0 && !filters.value.chains.includes(c.chain)) return false
    return true
  }).sort((a, b) => b.heatScore - a.heatScore)
})

function changeSign(v: number) {
  return v >= 0 ? '+' : ''
}
function changeClass(v: number) {
  return v >= 0 ? 'positive' : 'negative'
}

function resetFilters() {
  filters.value = { chains: [] }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
    <div class="text-center mb-8">
      <h1 class="text-3xl sm:text-4xl font-bold text-white">Advanced Filter</h1>
      <p class="text-crypto-400 mt-2 text-sm">Multi-dimensional filtering with real-time results</p>
    </div>

    <MemberGate>
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <!-- Filter Panel -->
        <div class="card lg:col-span-1 h-fit">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-white font-bold">Filters</h3>
            <button @click="resetFilters" class="text-xs text-crypto-400 hover:text-white transition-colors">Reset</button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="text-xs text-crypto-400 block mb-1">24h Change (%)</label>
              <div class="flex gap-2">
                <input v-model.number="filters.changeMin" type="number" placeholder="Min" class="w-full bg-crypto-700 border border-crypto-600 rounded px-2 py-1.5 text-xs text-white placeholder-crypto-500 focus:outline-none focus:border-accent" />
                <input v-model.number="filters.changeMax" type="number" placeholder="Max" class="w-full bg-crypto-700 border border-crypto-600 rounded px-2 py-1.5 text-xs text-white placeholder-crypto-500 focus:outline-none focus:border-accent" />
              </div>
            </div>

            <div>
              <label class="text-xs text-crypto-400 block mb-1">Volume (USD)</label>
              <div class="flex gap-2">
                <input v-model.number="filters.volumeMin" type="number" placeholder="Min" class="w-full bg-crypto-700 border border-crypto-600 rounded px-2 py-1.5 text-xs text-white placeholder-crypto-500 focus:outline-none focus:border-accent" />
                <input v-model.number="filters.volumeMax" type="number" placeholder="Max" class="w-full bg-crypto-700 border border-crypto-600 rounded px-2 py-1.5 text-xs text-white placeholder-crypto-500 focus:outline-none focus:border-accent" />
              </div>
            </div>

            <div>
              <label class="text-xs text-crypto-400 block mb-1">Market Cap (USD)</label>
              <div class="flex gap-2">
                <input v-model.number="filters.marketCapMin" type="number" placeholder="Min" class="w-full bg-crypto-700 border border-crypto-600 rounded px-2 py-1.5 text-xs text-white placeholder-crypto-500 focus:outline-none focus:border-accent" />
                <input v-model.number="filters.marketCapMax" type="number" placeholder="Max" class="w-full bg-crypto-700 border border-crypto-600 rounded px-2 py-1.5 text-xs text-white placeholder-crypto-500 focus:outline-none focus:border-accent" />
              </div>
            </div>

            <div>
              <label class="text-xs text-crypto-400 block mb-2">Chain</label>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="chain in chainOptions"
                  :key="chain"
                  @click="toggleChain(chain)"
                  class="text-xs px-2 py-1 rounded transition-colors"
                  :class="filters.chains?.includes(chain) ? 'bg-accent text-crypto-900' : 'bg-crypto-700 text-crypto-400 hover:text-white'"
                >
                  {{ chain }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Results -->
        <div class="lg:col-span-3">
          <div class="card">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-white font-bold">Results ({{ results.length }})</h3>
              <button class="btn-ghost text-xs" @click="store.saveStrategy({ id: Date.now().toString(), name: 'My Filter ' + new Date().toLocaleDateString(), filters: JSON.parse(JSON.stringify(filters)), alerts: false, createdAt: new Date().toISOString() })">
                Save as Strategy
              </button>
            </div>

            <div class="overflow-x-auto">
              <table class="table-base">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Price</th>
                    <th>24h</th>
                    <th>Volume</th>
                    <th>Market Cap</th>
                    <th>Heat</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="coin in results" :key="coin.id" class="cursor-pointer" @click="$router.push('/coin/' + coin.id)">
                    <td>
                      <div class="flex items-center gap-2">
                        <span class="font-medium text-white text-sm">{{ coin.symbol }}</span>
                        <span class="text-[10px] text-crypto-500">{{ coin.chain }}</span>
                      </div>
                    </td>
                    <td class="font-mono text-white text-sm">{{ formatPrice(coin.price) }}</td>
                    <td :class="changeClass(coin.change24h)" class="font-mono text-sm">
                      {{ changeSign(coin.change24h) }}{{ coin.change24h.toFixed(2) }}%
                    </td>
                    <td class="font-mono text-crypto-300 text-sm">{{ formatVolume(coin.volume) }}</td>
                    <td class="font-mono text-crypto-300 text-sm">{{ formatMarketCap(coin.marketCap) }}</td>
                    <td><HeatScore :score="coin.heatScore" size="sm" /></td>
                    <td><RiskBadge :level="coin.riskLevel" /></td>
                  </tr>
                  <tr v-if="results.length === 0">
                    <td colspan="7" class="text-center text-crypto-400 py-8 text-sm">No coins match your filters. Try adjusting the criteria.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Saved Strategies -->
          <div v-if="store.savedStrategies.length" class="card mt-4">
            <h3 class="text-white font-bold mb-3">Saved Strategies</h3>
            <div v-for="s in store.savedStrategies" :key="s.id" class="flex items-center justify-between py-2 border-b border-crypto-700 last:border-0">
              <div>
                <p class="text-sm text-white font-medium">{{ s.name }}</p>
                <p class="text-xs text-crypto-500">{{ new Date(s.createdAt).toLocaleDateString() }}</p>
              </div>
              <button @click="store.deleteStrategy(s.id)" class="text-xs text-hot hover:text-hot/80">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </MemberGate>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCryptoStore } from '@/stores/crypto'
import { timeAgo } from '@/data/mock'
import HeatScore from '@/components/HeatScore.vue'
import AdSlot from '@/components/AdSlot.vue'

const store = useCryptoStore()
const activeTab = ref<'heat' | 'media' | 'community' | 'event'>('heat')

const tabs = [
  { key: 'heat', label: 'Heat Rank' },
  { key: 'media', label: 'Media Mentions' },
  { key: 'community', label: 'Community' },
  { key: 'event', label: 'Events' },
] as const

const filteredTrends = computed(() => {
  const typeMap: Record<string, string> = {
    'heat': 'heat',
    'media': 'media',
    'community': 'community',
    'event': 'event',
  }
  return store.trends.filter(t => t.type === typeMap[activeTab.value])
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
    <div class="text-center mb-8">
      <h1 class="text-3xl sm:text-4xl font-bold text-white">Hot Trends</h1>
      <p class="text-crypto-400 mt-2 text-sm">Real-time crypto market trends across social, media, and communities</p>
    </div>

    <!-- Tab Bar -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        :class="activeTab === tab.key ? 'bg-accent text-crypto-900' : 'bg-crypto-700 text-crypto-300 hover:text-white'"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Trend List -->
    <div class="card mb-8">
      <div v-if="filteredTrends.length === 0" class="text-crypto-400 text-sm py-8 text-center">
        No trends found in this category
      </div>
      <div v-for="(item, idx) in filteredTrends" :key="item.id" class="flex items-start gap-4 py-4 border-b border-crypto-700 last:border-0">
        <span class="text-crypto-500 text-xs font-mono w-5">{{ idx + 1 }}</span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <h3 class="text-white font-semibold text-sm cursor-pointer hover:text-accent" @click="$router.push('/coin/' + item.coinId)">
              {{ item.title }}
            </h3>
            <span v-if="item.source" class="text-[10px] bg-crypto-700 text-crypto-400 px-1.5 py-0.5 rounded">{{ item.source }}</span>
          </div>
          <div class="flex items-center gap-3 text-xs text-crypto-500">
            <span class="font-medium text-crypto-300">{{ item.coinSymbol }}</span>
            <span>{{ timeAgo(item.timestamp) }}</span>
            <span v-if="item.change !== 0" :class="item.change > 0 ? 'positive' : 'negative'">
              {{ item.change > 0 ? '+' : '' }}{{ item.change.toFixed(1) }}%
            </span>
          </div>
          <div v-if="item.keywords && item.keywords.length" class="flex gap-1.5 mt-2 flex-wrap">
            <span v-for="kw in item.keywords" :key="kw" class="text-[10px] bg-crypto-700 text-crypto-400 px-1.5 py-0.5 rounded">
              #{{ kw }}
            </span>
          </div>
        </div>
        <div class="flex-shrink-0">
          <HeatScore :score="item.score" size="sm" />
        </div>
      </div>
    </div>

    <!-- Events Section (always show below) -->
    <div class="card mb-8">
      <h2 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
        <span>⚡</span> Major Events
      </h2>
      <div v-for="evt in store.alerts" :key="evt.id" class="py-3 border-b border-crypto-700 last:border-0">
        <div class="flex items-start gap-3">
          <span
            class="text-[10px] px-1.5 py-0.5 rounded font-medium mt-0.5"
            :class="evt.severity === 'high' ? 'bg-hot/20 text-hot' : evt.severity === 'medium' ? 'bg-warn/20 text-warn' : 'bg-accent/20 text-accent'"
          >
            {{ evt.severity.toUpperCase() }}
          </span>
          <div class="flex-1">
            <p class="text-sm text-white font-medium cursor-pointer hover:text-accent" @click="$router.push('/coin/' + evt.coinId)">{{ evt.title }}</p>
            <p v-if="evt.description" class="text-xs text-crypto-400 mt-1">{{ evt.description }}</p>
            <div class="flex items-center gap-3 mt-1 text-xs text-crypto-500">
              <span>{{ evt.coinSymbol }}</span>
              <span>{{ timeAgo(evt.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <AdSlot type="banner" />
  </div>
</template>

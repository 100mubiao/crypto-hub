<script setup lang="ts">
import { useCryptoStore } from '@/stores/crypto'

const store = useCryptoStore()

const endpoints = [
  {
    method: 'GET',
    path: '/api/v1/coins',
    description: 'List all tracked coins with real-time data',
    auth: 'Free (limited) / Premium',
    params: [
      { name: 'symbol', type: 'string', optional: true, desc: 'Filter by symbol (e.g., BTC)' },
      { name: 'chain', type: 'string', optional: true, desc: 'Filter by chain (ethereum, solana, bsc)' },
      { name: 'sort_by', type: 'string', optional: true, desc: 'Sort field (price, volume, change, heat)' },
      { name: 'limit', type: 'integer', optional: true, desc: 'Results per page (max 100)' },
    ],
    example: `curl https://api.cryptohub.dev/v1/coins?sort_by=heat&limit=10`,
  },
  {
    method: 'GET',
    path: '/api/v1/coins/:id',
    description: 'Get detailed data for a specific coin',
    auth: 'Free (limited) / Premium',
    params: [
      { name: 'id', type: 'string', optional: false, desc: 'Coin ID (e.g., bitcoin, ethereum)' },
    ],
    example: `curl https://api.cryptohub.dev/v1/coins/bitcoin`,
  },
  {
    method: 'GET',
    path: '/api/v1/trends',
    description: 'Get trending coins and hot topics',
    auth: 'Free',
    params: [
      { name: 'type', type: 'string', optional: true, desc: 'Trend type (heat, media, community, event)' },
      { name: 'timeframe', type: 'string', optional: true, desc: 'Time window (1h, 24h)' },
    ],
    example: `curl https://api.cryptohub.dev/v1/trends?type=heat`,
  },
  {
    method: 'GET',
    path: '/api/v1/new-coins',
    description: 'Get recently listed coins (new coin radar)',
    auth: 'Free (basic) / Premium (full)',
    params: [
      { name: 'hours', type: 'integer', optional: true, desc: 'Lookback window (default: 24)' },
      { name: 'potential', type: 'boolean', optional: true, desc: 'Filter AI-predicted potential gems' },
    ],
    example: `curl https://api.cryptohub.dev/v1/new-coins?potential=true`,
  },
  {
    method: 'GET',
    path: '/api/v1/alerts',
    description: 'Get recent major events and alerts',
    auth: 'Premium',
    params: [
      { name: 'severity', type: 'string', optional: true, desc: 'Filter by severity (high, medium, low)' },
      { name: 'limit', type: 'integer', optional: true, desc: 'Max results (default: 20)' },
    ],
    example: `curl https://api.cryptohub.dev/v1/alerts?severity=high`,
  },
]
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 py-6">
    <div class="mb-8">
      <h1 class="text-3xl sm:text-4xl font-bold text-white">API Documentation</h1>
      <p class="text-crypto-400 mt-2 text-sm">Access real-time cryptocurrency data programmatically</p>
    </div>

    <!-- Auth -->
    <div class="card mb-8">
      <h2 class="text-lg font-bold text-white mb-3">Authentication</h2>
      <p class="text-sm text-crypto-300 mb-3">Include your API key in the request header:</p>
      <div class="bg-crypto-900 rounded-lg p-3 font-mono text-sm text-crypto-200">
        X-API-Key: your_api_key_here
      </div>
      <p class="text-sm text-crypto-400 mt-3">
        Free tier: 100 requests/day &middot; Premium: 1,000 requests/day &middot;
        <router-link to="/pricing" class="text-accent hover:underline">Upgrade for more</router-link>
      </p>
    </div>

    <!-- Base URL -->
    <div class="card mb-8">
      <h2 class="text-lg font-bold text-white mb-3">Base URL</h2>
      <div class="bg-crypto-900 rounded-lg p-3 font-mono text-sm text-crypto-200">
        https://api.cryptohub.dev/v1
      </div>
    </div>

    <!-- Endpoints -->
    <div class="space-y-4 mb-8">
      <div v-for="ep in endpoints" :key="ep.path" class="card">
        <div class="flex items-center gap-3 mb-3">
          <span
            class="text-xs font-bold px-2 py-0.5 rounded"
            :class="ep.method === 'GET' ? 'bg-accent/20 text-accent' : 'bg-accent/20 text-accent'"
          >
            {{ ep.method }}
          </span>
          <code class="text-sm text-white font-mono bg-crypto-900 px-2 py-1 rounded">{{ ep.path }}</code>
          <span class="text-[10px] text-crypto-500 ml-auto">{{ ep.auth }}</span>
        </div>
        <p class="text-sm text-crypto-300 mb-3">{{ ep.description }}</p>

        <div v-if="ep.params.length" class="mb-3">
          <p class="text-xs text-crypto-400 mb-2 font-medium">Parameters</p>
          <div class="space-y-1">
            <div v-for="param in ep.params" :key="param.name" class="flex gap-4 text-xs">
              <span class="font-mono text-crypto-200 w-28">{{ param.name }}</span>
              <span class="text-crypto-500 w-16">{{ param.type }}</span>
              <span class="text-crypto-500 w-14">{{ param.optional ? 'optional' : 'required' }}</span>
              <span class="text-crypto-400 flex-1">{{ param.desc }}</span>
            </div>
          </div>
        </div>

        <div>
          <p class="text-xs text-crypto-400 mb-1 font-medium">Example</p>
          <div class="bg-crypto-900 rounded-lg p-3 font-mono text-xs text-crypto-200 break-all">
            {{ ep.example }}
          </div>
        </div>
      </div>
    </div>

    <!-- Rate Limits -->
    <div class="card mb-8">
      <h2 class="text-lg font-bold text-white mb-3">Rate Limits</h2>
      <div class="space-y-2 text-sm">
        <div class="flex justify-between py-1 border-b border-crypto-700">
          <span class="text-crypto-300">Free Tier</span>
          <span class="text-white font-mono">100 requests / day</span>
        </div>
        <div class="flex justify-between py-1 border-b border-crypto-700">
          <span class="text-crypto-300">Premium</span>
          <span class="text-white font-mono">1,000 requests / day</span>
        </div>
        <div class="flex justify-between py-1 border-b border-crypto-700">
          <span class="text-crypto-300">Enterprise</span>
          <span class="text-white font-mono">Custom</span>
        </div>
        <div class="flex justify-between py-1">
          <span class="text-crypto-300">Rate window</span>
          <span class="text-white font-mono">Rolling 24h</span>
        </div>
      </div>
    </div>

    <!-- Response Format -->
    <div class="card mb-8">
      <h2 class="text-lg font-bold text-white mb-3">Response Format</h2>
      <p class="text-sm text-crypto-300 mb-3">All responses are in JSON format:</p>
      <div class="bg-crypto-900 rounded-lg p-3 font-mono text-xs text-crypto-200">
        <pre>{
  "status": "ok",
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 10,
    "total": 142
  }
}</pre>
      </div>
    </div>

    <div class="card text-center">
      <h2 class="text-lg font-bold text-white mb-2">Ready to integrate?</h2>
      <p class="text-sm text-crypto-400 mb-4">Get your API key and start building</p>
      <div class="flex gap-3 justify-center">
        <button v-if="!store.isMember" @click="$router.push('/pricing')" class="btn-primary">Get API Access</button>
        <router-link to="/" class="btn-ghost">Back to Dashboard</router-link>
      </div>
    </div>
  </div>
</template>

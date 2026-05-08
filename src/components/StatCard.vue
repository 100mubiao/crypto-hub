<script setup lang="ts">
defineProps<{
  title: string
  value: string
  change?: string
  trend?: 'up' | 'down' | 'neutral'
  icon?: string
}>()
</script>

<template>
  <div class="card">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-crypto-400 text-xs font-medium uppercase tracking-wider">{{ title }}</p>
        <p class="text-xl font-bold text-white mt-1">{{ value }}</p>
      </div>
      <span v-if="icon" class="text-2xl">{{ icon }}</span>
    </div>
    <div v-if="change" class="mt-2 flex items-center gap-1">
      <span
        class="text-xs font-medium"
        :class="trend === 'up' ? 'positive' : trend === 'down' ? 'negative' : 'text-crypto-400'"
      >
        {{ trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→' }} {{ change }}
      </span>
      <span class="text-crypto-500 text-xs">vs 24h ago</span>
    </div>
  </div>
</template>

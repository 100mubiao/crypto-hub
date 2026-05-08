<script setup lang="ts">
import { useCryptoStore } from '@/stores/crypto'

defineProps<{
  type?: 'banner' | 'sidebar' | 'native' | 'promoted'
  label?: string
}>()

const store = useCryptoStore()
</script>

<template>
  <div
    v-if="!store.isMember"
    class="border border-dashed border-crypto-500 rounded-lg bg-crypto-800/50 flex items-center justify-center text-center p-4"
    :class="type === 'banner' ? 'min-h-[90px]' : type === 'sidebar' ? 'min-h-[250px]' : type === 'native' ? 'min-h-[100px]' : 'min-h-[80px]'"
  >
    <div>
      <p class="text-xs text-crypto-500 mb-1">{{ label || 'Sponsored' }}</p>
      <p class="text-sm text-crypto-400">Advertisement Space</p>
    </div>
  </div>
</template>

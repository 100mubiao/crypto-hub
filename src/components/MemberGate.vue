<script setup lang="ts">
import { useCryptoStore } from '@/stores/crypto'
import { useRouter } from 'vue-router'

const store = useCryptoStore()
const router = useRouter()
</script>

<template>
  <div v-if="!store.isMember" class="card border-accent/30 text-center py-8">
    <div class="text-4xl mb-3">&#128274;</div>
    <h3 class="text-lg font-bold text-white mb-2">Premium Feature</h3>
    <p class="text-crypto-400 text-sm mb-4 max-w-md mx-auto">
      Upgrade to Premium to unlock advanced filters, custom strategies, real-time alerts, and in-depth on-chain data.
    </p>
    <button @click="router.push('/pricing')" class="btn-primary">
      View Plans
    </button>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { useCryptoStore } from '@/stores/crypto'
import { useRouter } from 'vue-router'

const store = useCryptoStore()
const router = useRouter()

const themes = [
  { id: 'default', label: 'Classic', desc: 'Original CryptoHub dark theme' },
  { id: 'neon', label: 'Neon Pulse', desc: 'Purple-cyan neon glow' },
]
</script>

<template>
  <div v-if="!store.isMember" class="card border-accent/30 text-center py-6">
    <div class="text-4xl mb-3">🎨</div>
    <h3 class="text-lg font-bold text-white mb-2">Premium Themes</h3>
    <p class="text-crypto-400 text-sm mb-4 max-w-md mx-auto">
      Unlock exclusive visual themes and customize your CryptoHub experience.
    </p>
    <button @click="router.push('/pricing')" class="btn-primary">
      Upgrade to Premium
    </button>
  </div>

  <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
    <button
      v-for="t in themes"
      :key="t.id"
      @click="store.setTheme(t.id)"
      class="card text-left cursor-pointer transition-all duration-200"
      :class="store.theme === t.id ? 'border-accent ring-1 ring-accent/30' : 'opacity-70 hover:opacity-100'"
    >
      <div class="flex items-center gap-3 mb-2">
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
          :class="t.id === 'neon' ? 'bg-purple-500/20 text-purple-400' : 'bg-accent/20 text-accent'"
        >
          {{ t.id === 'neon' ? 'N' : 'C' }}
        </div>
        <div>
          <p class="text-white font-semibold text-sm">{{ t.label }}</p>
          <p class="text-crypto-400 text-xs">{{ t.desc }}</p>
        </div>
      </div>
      <div v-if="store.theme === t.id" class="text-accent text-xs font-medium">Active</div>
    </button>
  </div>
</template>

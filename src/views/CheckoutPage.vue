<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'

const router = useRouter()
const route = useRoute()
const store = useCryptoStore()

const plans: Record<string, { label: string; price: string; apiKey: string }> = {
  'Premium Monthly': { label: 'Premium Monthly', price: '$0.99', apiKey: 'premium_monthly' },
  'Lifetime': { label: 'Lifetime', price: '$9.9', apiKey: 'lifetime' },
}

const planName = computed(() => {
  const raw = route.params.plan as string
  return decodeURIComponent(raw)
})

const plan = computed(() => plans[planName.value])

const loading = ref(false)
const done = ref(false)
const error = ref('')

async function pay() {
  if (!plan.value) return
  error.value = ''
  loading.value = true
  try {
    await store.purchase(plan.value.apiKey)
    done.value = true
  } catch {
    error.value = 'Payment failed. Please try again.'
  } finally {
    loading.value = false
  }
}

function goHome() {
  router.push('/')
}
</script>

<template>
  <div class="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
    <div class="w-full max-w-md card p-8 text-center" v-if="!done">
      <h1 class="text-2xl font-bold text-white mb-2">Complete Purchase</h1>
      <p class="text-crypto-400 text-sm mb-6">You are about to purchase the following plan</p>

      <div class="bg-crypto-800 rounded-lg p-4 mb-6" v-if="plan">
        <p class="text-lg font-bold text-white">{{ plan.label }}</p>
        <p class="text-3xl font-bold text-accent mt-1">{{ plan.price }}</p>
        <p v-if="plan.apiKey === 'lifetime'" class="text-crypto-400 text-xs mt-1">One-time payment, no recurring fees</p>
        <p v-else class="text-crypto-400 text-xs mt-1">Billed monthly, cancel anytime</p>
      </div>
      <p v-else class="text-hot text-sm">Invalid plan selected.</p>

      <p v-if="error" class="text-hot text-sm mb-4">{{ error }}</p>

      <div class="space-y-3" v-if="plan">
        <button @click="pay" :disabled="loading" class="btn-primary w-full">
          {{ loading ? 'Processing...' : 'Pay ' + plan.price }}
        </button>
        <button @click="router.back()" class="btn-ghost w-full">Cancel</button>
      </div>
    </div>

    <div class="w-full max-w-md card p-8 text-center" v-else>
      <div class="text-5xl mb-4">&#10003;</div>
      <h1 class="text-2xl font-bold text-white mb-2">Payment Successful!</h1>
      <p class="text-crypto-400 text-sm mb-6" v-if="plan">
        You now have access to {{ plan.label }} features.
      </p>
      <button @click="goHome" class="btn-primary w-full">Go to Dashboard</button>
    </div>
  </div>
</template>

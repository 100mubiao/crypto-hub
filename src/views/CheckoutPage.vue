<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'
import { apiCreateCheckoutSession, apiGetPaymentSuccess } from '@/api'

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
const canceled = ref(route.query.canceled === 'true')
const sessionId = ref(route.query.session_id as string || '')

onMounted(async () => {
  // Success redirect from Stripe: verify session
  if (sessionId.value) {
    loading.value = true
    try {
      const res = await apiGetPaymentSuccess(sessionId.value)
      if (res) {
        await store.restoreSession()
        done.value = true
      } else {
        error.value = 'Could not verify payment. Please contact support.'
      }
    } catch {
      error.value = 'Verification failed.'
    } finally {
      loading.value = false
    }
  }
})

async function payWithStripe() {
  if (!plan.value) return
  error.value = ''
  loading.value = true
  try {
    const res = await apiCreateCheckoutSession(plan.value.apiKey)
    if (res?.url) {
      // Redirect to Stripe Checkout
      window.location.href = res.url
    } else {
      error.value = 'Failed to create checkout session. Please try again.'
    }
  } catch {
    error.value = 'Payment service error.'
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
    <!-- Cancelled -->
    <div v-if="canceled" class="w-full max-w-md card p-8 text-center">
      <div class="text-5xl mb-4">&#10060;</div>
      <h1 class="text-2xl font-bold text-white mb-2">Payment Cancelled</h1>
      <p class="text-crypto-400 text-sm mb-6">Your payment was not completed. No charges were made.</p>
      <button @click="goHome" class="btn-primary w-full">Back to Home</button>
    </div>

    <!-- Success -->
    <div v-else-if="done" class="w-full max-w-md card p-8 text-center">
      <div class="text-5xl mb-4">&#10003;</div>
      <h1 class="text-2xl font-bold text-white mb-2">Payment Successful!</h1>
      <p class="text-green-400 text-sm mb-6">
        Your membership has been upgraded. You now have access to all {{ plan?.label }} features.
      </p>
      <button @click="goHome" class="btn-primary w-full">Go to Dashboard</button>
    </div>

    <!-- Loading (during success verification) -->
    <div v-else-if="sessionId && loading" class="w-full max-w-md card p-8 text-center">
      <div class="animate-spin text-4xl mb-4">&#8987;</div>
      <p class="text-crypto-400 text-sm">Verifying your payment...</p>
    </div>

    <!-- Checkout form -->
    <div v-else class="w-full max-w-md card p-8 text-center">
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
        <button @click="payWithStripe" :disabled="loading" class="btn-primary w-full">
          {{ loading ? 'Redirecting to Stripe...' : 'Pay with Stripe' }}
        </button>
        <button @click="router.back()" class="btn-ghost w-full">Cancel</button>
      </div>

      <p class="text-crypto-500 text-xs mt-4">Secured by Stripe. Your payment info is never stored on our servers.</p>
    </div>
  </div>
</template>

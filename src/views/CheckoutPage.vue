<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'
import { apiCreateCheckoutSession, apiGetPaymentSuccess, apiCreatePayPalOrder, apiCapturePayPalOrder } from '@/api'

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
const paypalReady = ref(false)
const paypalLoading = ref(false)
const paypalOrderId = ref('')
let paypalButtonsRendered = false

onMounted(async () => {
  // Handle PayPal success redirect
  if (route.query.paypal === 'success' && route.query.token) {
    loading.value = true
    try {
      const res = await apiCapturePayPalOrder(route.query.token as string)
      if (res) {
        await store.restoreSession()
        done.value = true
      } else {
        error.value = 'Could not verify payment. Please contact support.'
      }
    } catch {
      error.value = 'PayPal verification failed.'
    } finally {
      loading.value = false
    }
    return
  }

  // Handle Stripe success redirect: verify session
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
    return
  }

  // Load PayPal SDK for checkout form
  await loadPayPalSDK()
})

async function loadPayPalSDK() {
  if (document.getElementById('paypal-sdk')) {
    paypalReady.value = true
    return
  }
  const VITE_API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
  // Fetch client ID from backend status endpoint (fallback to a config approach)
  let clientId = ''
  try {
    const res = await fetch(`${VITE_API_BASE}/api/v1/payment/paypal/client-id`, {
      signal: AbortSignal.timeout(5000),
    })
    if (res.ok) {
      const data = await res.json()
      clientId = data.client_id
    }
  } catch {
    // Fallback: will show error when user clicks PayPal
  }

  if (!clientId) {
    paypalReady.value = true // allow user to try, error will show on click
    return
  }

  const script = document.createElement('script')
  script.id = 'paypal-sdk'
  script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=USD&intent=capture`
  script.onload = () => {
    paypalReady.value = true
    nextTick(() => renderPayPalButtons())
  }
  document.body.appendChild(script)
}

function renderPayPalButtons() {
  if (paypalButtonsRendered || typeof (window as any).paypal === 'undefined') return
  const container = document.getElementById('paypal-button-container')
  if (!container) return

  paypalButtonsRendered = true
  ;(window as any).paypal.Buttons({
    createOrder: async () => {
      paypalLoading.value = true
      error.value = ''
      try {
        const res = await apiCreatePayPalOrder(plan.value!.apiKey)
        if (!res?.order_id) throw new Error('Failed to create order')
        paypalOrderId.value = res.order_id
        return res.order_id
      } catch (e) {
        error.value = 'Failed to create PayPal order.'
        paypalLoading.value = false
        throw e
      }
    },
    onApprove: async (data: { orderID: string }) => {
      try {
        const res = await apiCapturePayPalOrder(data.orderID)
        if (res) {
          await store.restoreSession()
          done.value = true
        } else {
          error.value = 'Payment verification failed. Please contact support.'
        }
      } catch {
        error.value = 'Failed to complete PayPal payment.'
      } finally {
        paypalLoading.value = false
      }
    },
    onCancel: () => {
      error.value = 'PayPal payment was cancelled.'
      paypalLoading.value = false
    },
    onError: () => {
      error.value = 'PayPal encountered an error. Please try again.'
      paypalLoading.value = false
    },
  }).render('#paypal-button-container')
}

async function payWithStripe() {
  if (!plan.value) return
  error.value = ''
  loading.value = true
  try {
    const res = await apiCreateCheckoutSession(plan.value.apiKey)
    if (res?.url) {
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
        <button @click="payWithStripe" :disabled="loading || paypalLoading" class="btn-primary w-full flex items-center justify-center gap-2">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M13.976 9.15c-2.172-.806-3.356-1.426-3.356-2.409 0-.831.683-1.305 1.901-1.305 1.672 0 3.063.683 4.037 1.275l1.1-2.431C16.532 3.654 14.88 3 12.977 3 9.764 3 7.3 4.922 7.3 7.725c0 2.357 1.86 3.702 4.347 4.617 2.2.81 3.407 1.426 3.407 2.514 0 .882-.738 1.391-2.064 1.391-1.702 0-3.386-.779-4.405-1.462l-1.22 2.478c1.29.997 3.049 1.651 5.1 1.651 3.458 0 5.968-1.978 5.968-4.73 0-2.585-1.916-3.916-4.547-4.873l.009-.006z"/></svg>
          {{ loading ? 'Redirecting...' : 'Pay with Card (Stripe)' }}
        </button>

        <div class="relative flex items-center py-2">
          <div class="flex-grow border-t border-crypto-700"></div>
          <span class="flex-shrink mx-3 text-crypto-500 text-xs">or pay with</span>
          <div class="flex-grow border-t border-crypto-700"></div>
        </div>

        <div v-if="paypalReady" id="paypal-button-container" class="min-h-[40px]"></div>
        <div v-else class="text-center py-2">
          <span class="text-crypto-500 text-sm">Loading PayPal...</span>
        </div>

        <button @click="router.back()" class="btn-ghost w-full">Cancel</button>
      </div>

      <p class="text-crypto-500 text-xs mt-4">Secured by Stripe & PayPal. Your payment info is never stored on our servers.</p>
    </div>
  </div>
</template>

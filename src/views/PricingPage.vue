<script setup lang="ts">
import { useCryptoStore } from '@/stores/crypto'
import { useRouter } from 'vue-router'

const store = useCryptoStore()
const router = useRouter()

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Essential data for casual investors',
    features: [
      'Real-time price data',
      'Basic filtering',
      "Today's new coins",
      'Hot trends (basic)',
      'Coin detail pages',
      'Standard ads',
    ],
    cta: 'Get Started',
    highlighted: false,
  },
  {
    name: 'Premium Monthly',
    price: '$0.99',
    period: '/month',
    description: 'Advanced tools for serious traders',
    features: [
      'Everything in Free',
      'Ad-free experience',
      'Advanced multi-filter',
      'Custom strategies & alerts',
      'On-chain & depth data',
      'New coin radar (early access)',
      'Priority event alerts',
      'Data export (CSV)',
    ],
    cta: 'Subscribe',
    highlighted: true,
  },
  {
    name: 'Lifetime',
    price: '$9.9',
    period: 'one-time',
    description: 'Pay once, own it forever',
    features: [
      'Everything in Premium Monthly',
      'No recurring fees',
      'API access (5000 req/day)',
      'Priority support',
      'Exclusive analysis reports',
      'Early access to new features',
    ],
    cta: 'Buy Lifetime',
    highlighted: false,
  },
]

function selectPlan(name: string) {
  if (name === 'Free') {
    router.push('/register')
    return
  }
  if (!store.token) {
    router.push('/login?redirect=/checkout/' + encodeURIComponent(name))
    return
  }
  router.push('/checkout/' + encodeURIComponent(name))
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
    <div class="text-center mb-10">
      <h1 class="text-3xl sm:text-4xl font-bold text-white">Choose Your Plan</h1>
      <p class="text-crypto-400 mt-2 text-sm">Unlock the full power of CryptoHub data aggregation</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
      <div
        v-for="plan in plans"
        :key="plan.name"
        class="card flex flex-col relative"
        :class="plan.highlighted ? 'border-accent ring-1 ring-accent/30' : ''"
      >
        <div v-if="plan.highlighted" class="absolute -top-3 left-1/2 -translate-x-1/2 bg-accent text-crypto-900 text-xs font-bold px-3 py-1 rounded-full">
          Most Popular
        </div>

        <div class="mb-6">
          <h3 class="text-xl font-bold text-white">{{ plan.name }}</h3>
          <div class="mt-2 flex items-baseline gap-1">
            <span class="text-3xl font-bold text-white">{{ plan.price }}</span>
            <span class="text-crypto-400 text-sm">{{ plan.period }}</span>
          </div>
          <p class="text-crypto-400 text-sm mt-2">{{ plan.description }}</p>
        </div>

        <ul class="space-y-3 flex-1 mb-6">
          <li v-for="feature in plan.features" :key="feature" class="flex items-start gap-2 text-sm">
            <span class="text-accent mt-0.5">&#10003;</span>
            <span class="text-crypto-300">{{ feature }}</span>
          </li>
        </ul>

        <button
          @click="selectPlan(plan.name)"
          class="w-full py-2.5 rounded-lg font-semibold text-sm transition-all"
          :class="plan.highlighted
            ? 'bg-accent text-crypto-900 hover:bg-accent-hover'
            : 'bg-crypto-700 text-white hover:bg-crypto-600'"
        >
          {{ plan.cta }}
        </button>
      </div>
    </div>

    <div class="card mt-8 max-w-5xl mx-auto text-center">
      <h3 class="text-white font-bold text-lg mb-2">Need Enterprise Access?</h3>
      <p class="text-crypto-400 text-sm mb-4">Higher API rate limits, dedicated support, custom integrations.</p>
      <button class="btn-ghost">Contact Sales</button>
    </div>

    <div class="max-w-5xl mx-auto mt-8">
      <div class="bg-hot/5 border border-hot/10 rounded-lg p-4 text-center">
        <p class="text-xs text-crypto-500">
          &#9888;&#65039; CryptoHub provides data aggregation services only. We do not offer trading, investment advice, or financial services.
          Cryptocurrency investments carry high risk. Past performance does not guarantee future results.
          This service is not available to users in restricted jurisdictions.
        </p>
      </div>
    </div>
  </div>
</template>

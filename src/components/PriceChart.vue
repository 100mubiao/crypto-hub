<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { createChart, ColorType, CandlestickSeries, type IChartApi, type CandlestickSeriesPartialOptions } from 'lightweight-charts'
import type { ApiOhlcPoint } from '@/api'

const props = defineProps<{
  coinId: string
  fetchFn: (coinId: string, days: number) => Promise<ApiOhlcPoint[] | null>
}>()

const periods = [
  { label: '1D', days: 1 },
  { label: '7D', days: 7 },
  { label: '1M', days: 30 },
  { label: '1Y', days: 365 },
] as const

const activePeriod = ref(7)
const loading = ref(true)
const noData = ref(false)

const containerRef = ref<HTMLDivElement | null>(null)
let chart: IChartApi | null = null
let resizeObserver: ResizeObserver | null = null

const seriesOptions: CandlestickSeriesPartialOptions = {
  upColor: '#00c897',
  downColor: '#ff6b6b',
  borderDownColor: '#ff6b6b',
  borderUpColor: '#00c897',
  wickDownColor: '#ff6b6b',
  wickUpColor: '#00c897',
}

function adaptData(raw: ApiOhlcPoint[]) {
  return raw.map(p => ({
    time: p.time as any,
    open: p.open,
    high: p.high,
    low: p.low,
    close: p.close,
  }))
}

async function loadData(days: number) {
  loading.value = true
  noData.value = false
  const raw = await props.fetchFn(props.coinId, days)
  if (!raw || raw.length === 0) {
    noData.value = true
    loading.value = false
    return
  }
  const data = adaptData(raw)
  loading.value = false

  if (!chart) return
  const series = chart.addSeries(CandlestickSeries, seriesOptions)
  series.setData(data)
  chart.timeScale().fitContent()
}

function initChart() {
  if (!containerRef.value) return
  const container = containerRef.value

  chart = createChart(container, {
    layout: {
      background: { type: ColorType.Solid, color: '#1a1a2e' },
      textColor: '#6c6ca0',
    },
    grid: {
      vertLines: { color: '#2d2d56' },
      horzLines: { color: '#2d2d56' },
    },
    width: container.clientWidth,
    height: 360,
    crosshair: {
      mode: 0,
    },
    rightPriceScale: {
      borderColor: '#2d2d56',
    },
    timeScale: {
      borderColor: '#2d2d56',
      timeVisible: true,
      secondsVisible: false,
    },
  })

  resizeObserver = new ResizeObserver(() => {
    if (chart && container) {
      chart.applyOptions({ width: container.clientWidth })
    }
  })
  resizeObserver.observe(container)

  loadData(activePeriod.value)
}

function switchPeriod(days: number) {
  if (days === activePeriod.value) return
  activePeriod.value = days
  if (chart) {
    chart.remove()
    chart = null
  }
  initChart()
}

onMounted(initChart)

onUnmounted(() => {
  resizeObserver?.disconnect()
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-white font-bold">Price Chart</h3>
      <div class="flex gap-1">
        <button
          v-for="p in periods"
          :key="p.days"
          @click="switchPeriod(p.days)"
          class="px-2.5 py-1 text-xs rounded font-medium transition-colors"
          :class="activePeriod === p.days ? 'bg-accent text-crypto-900' : 'bg-crypto-700 text-crypto-400 hover:text-white'"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <div ref="containerRef" class="relative">
      <div
        v-if="loading"
        class="absolute inset-0 flex items-center justify-center bg-crypto-800/60 rounded-lg z-10"
      >
        <div class="flex flex-col items-center gap-2">
          <div class="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin"></div>
          <p class="text-crypto-400 text-xs">Loading chart...</p>
        </div>
      </div>
      <div
        v-if="noData"
        class="absolute inset-0 flex items-center justify-center bg-crypto-800/60 rounded-lg z-10"
      >
        <p class="text-crypto-400 text-sm">Chart data unavailable for this period</p>
      </div>
    </div>
  </div>
</template>

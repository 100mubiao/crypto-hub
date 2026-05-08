<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  size?: 'sm' | 'md'
}>()

const color = computed(() => {
  if (props.score >= 8) return '#ff6b6b'
  if (props.score >= 6) return '#ff8c00'
  if (props.score >= 4) return '#ffd700'
  return '#4ecdc4'
})

const barWidth = computed(() => Math.min(100, Math.max(0, props.score * 10)))
</script>

<template>
  <div class="flex items-center gap-2">
    <div class="bg-crypto-700 rounded-full overflow-hidden" :class="size === 'sm' ? 'w-12 h-1.5' : 'w-16 h-2'">
      <div
        class="h-full rounded-full transition-all duration-500"
        :style="{ width: barWidth + '%', background: color }"
      />
    </div>
    <span class="font-bold" :class="size === 'sm' ? 'text-xs' : 'text-sm'" :style="{ color }">
      {{ score.toFixed(1) }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  level: 'low' | 'medium' | 'high'
}>()

const config = computed(() => {
  switch (props.level) {
    case 'low': return { label: 'Low Risk', class: 'bg-accent/15 text-accent border-accent/20' }
    case 'medium': return { label: 'Medium Risk', class: 'bg-warn/15 text-warn border-warn/20' }
    case 'high': return { label: 'High Risk', class: 'bg-hot/15 text-hot border-hot/20' }
  }
})
</script>

<template>
  <span class="text-xs font-medium px-2 py-0.5 rounded border" :class="config.class">
    {{ config.label }}
  </span>
</template>

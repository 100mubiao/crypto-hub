<script setup lang="ts">
import { onMounted } from 'vue'
import { useCryptoStore } from '@/stores/crypto'
import NavBar from './NavBar.vue'
import FooterSection from './FooterSection.vue'
import ComplianceBanner from './ComplianceBanner.vue'

const store = useCryptoStore()

onMounted(() => {
  store.initialize()
})
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <ComplianceBanner />
    <NavBar />
    <main class="flex-1">
      <router-view />
    </main>
    <FooterSection />
  </div>
</template>

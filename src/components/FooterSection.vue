<script setup lang="ts">
</script>

<template>
  <footer class="border-t border-crypto-700 bg-crypto-800/50 mt-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-10">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-7 h-7 bg-accent rounded-lg flex items-center justify-center text-crypto-900 text-xs font-bold">C</span>
            <span class="text-lg font-bold text-gradient">CryptoHub</span>
          </div>
          <p class="text-crypto-400 text-sm leading-relaxed">
            Real-time cryptocurrency data aggregation. Focus on what matters: newest, hottest, most active coins.
          </p>
        </div>
        <div>
          <h4 class="text-white font-semibold text-sm mb-3">Product</h4>
          <ul class="space-y-2 text-sm text-crypto-400">
            <li><router-link to="/" class="hover:text-accent transition-colors">Dashboard</router-link></li>
            <li><router-link to="/trends" class="hover:text-accent transition-colors">Trends</router-link></li>
            <li><router-link to="/advanced-filter" class="hover:text-accent transition-colors">Advanced Filter</router-link></li>
            <li><router-link to="/pricing" class="hover:text-accent transition-colors">Pricing</router-link></li>
            <li><a href="https://github.com/100mubiao/Crypto-hub/releases/latest" target="_blank" rel="noopener" class="hover:text-accent transition-colors flex items-center gap-1">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
              Download App
            </a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold text-sm mb-3">Company</h4>
          <ul class="space-y-2 text-sm text-crypto-400">
            <li><router-link to="/about" class="hover:text-accent transition-colors">About Us</router-link></li>
            <li><router-link to="/contact" class="hover:text-accent transition-colors">Contact Us</router-link></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold text-sm mb-3">Legal</h4>
          <ul class="space-y-2 text-sm text-crypto-400">
            <li><router-link to="/privacy" class="hover:text-accent transition-colors">Privacy Policy</router-link></li>
            <li><a href="#" class="hover:text-accent transition-colors">Terms of Service</a></li>
            <li><a href="#" class="hover:text-accent transition-colors">Risk Disclaimer</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-crypto-700 mt-8 pt-6 text-center text-xs text-crypto-500">
        <p>CryptoHub is a data aggregation tool only. Not financial advice. Cryptocurrency investments carry high risk.</p>
        <p class="mt-1">&copy; 2026 CryptoHub. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

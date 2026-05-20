<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'

const router = useRouter()
const store = useCryptoStore()
const mobileMenu = ref(false)
const showUserMenu = ref(false)
const showThemePanel = ref(false)

const navLinks = [
  { label: 'Dashboard', path: '/' },
  { label: 'Trends', path: '/trends' },
  { label: 'Advanced Filter', path: '/advanced-filter' },
  { label: 'Pricing', path: '/pricing' },
]
</script>

<template>
  <header class="sticky top-0 z-50 bg-crypto-900/90 backdrop-blur-lg border-b border-crypto-700">
    <div class="max-w-7xl mx-auto px-4 sm:px-6">
      <div class="flex items-center justify-between h-16">
        <router-link to="/" class="flex items-center gap-2 text-xl font-bold">
          <span class="w-8 h-8 bg-accent rounded-lg flex items-center justify-center text-crypto-900 text-sm font-bold">C</span>
          <span class="text-gradient">CryptoHub</span>
        </router-link>

        <nav class="hidden md:flex items-center gap-1">
          <router-link
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="px-3 py-2 text-sm rounded-lg transition-colors"
            :class="$route.path === link.path ? 'bg-crypto-700 text-white' : 'text-crypto-300 hover:text-white hover:bg-crypto-700/50'"
          >
            {{ link.label }}
          </router-link>
        </nav>

        <div class="flex items-center gap-3">
          <span
            v-if="store.loading"
            class="text-[10px] text-crypto-400 animate-pulse hidden sm:block"
          >
            Loading...
          </span>
          <span
            v-else-if="!store.usingMock"
            class="text-[10px] bg-accent/10 text-accent px-2 py-0.5 rounded hidden sm:block"
          >
            Live
          </span>
          <span
            v-else
            class="text-[10px] bg-warn/10 text-warn px-2 py-0.5 rounded hidden sm:block"
          >
            Demo
          </span>

          <template v-if="store.user">
            <button
              v-if="!store.isMember"
              @click="router.push('/pricing')"
              class="btn-primary text-sm hidden sm:block"
            >
              Get Premium
            </button>
            <button
              v-else
              class="text-xs bg-gold/20 text-gold px-3 py-1.5 rounded-lg hidden sm:block"
            >
              &#9733; Premium
            </button>
            <div class="relative hidden sm:block">
              <button @click="showUserMenu = !showUserMenu" class="flex items-center gap-1 text-crypto-300 hover:text-white text-sm px-2 py-1 rounded-lg hover:bg-crypto-700/50 transition-colors">
                <span class="w-6 h-6 bg-accent/20 text-accent rounded-full flex items-center justify-center text-xs font-bold">{{ store.user.name.charAt(0).toUpperCase() }}</span>
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
              </button>
              <div v-if="showUserMenu" class="absolute right-0 mt-2 w-56 bg-crypto-800 border border-crypto-700 rounded-lg shadow-lg py-1 z-50" @click.outside="showUserMenu = false">
                <div class="px-3 py-2 text-xs text-crypto-400 border-b border-crypto-700">{{ store.user.email }}</div>
                <button v-if="store.isMember" @click="showThemePanel = !showThemePanel; showUserMenu = false" class="w-full text-left px-3 py-2 text-sm text-crypto-300 hover:bg-crypto-700 hover:text-white transition-colors flex items-center gap-2">
                  <span>🎨</span> Themes
                </button>
                <button @click="store.logout(); showUserMenu = false; router.push('/')" class="w-full text-left px-3 py-2 text-sm text-crypto-300 hover:bg-crypto-700 hover:text-white transition-colors">Sign Out</button>
              </div>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="text-sm text-crypto-300 hover:text-white hidden sm:block">Sign In</router-link>
            <router-link to="/register" class="btn-primary text-sm hidden sm:block">Sign Up</router-link>
          </template>

          <button @click="mobileMenu = !mobileMenu" class="md:hidden text-crypto-300 p-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="!mobileMenu" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="mobileMenu" class="md:hidden border-t border-crypto-700">
        <div class="py-2 space-y-0.5">
          <router-link
            v-for="link in navLinks"
            :key="link.path"
            :to="link.path"
            class="block px-4 py-3 text-sm font-medium rounded-lg mx-2"
            :class="$route.path === link.path ? 'bg-crypto-700 text-white' : 'text-crypto-300 hover:bg-crypto-700/50'"
            @click="mobileMenu = false"
          >
            {{ link.label }}
          </router-link>
        </div>
        <div class="border-t border-crypto-700 py-2">
          <template v-if="store.user">
            <div class="px-4 py-2 text-xs text-crypto-400 truncate">{{ store.user.email }}</div>
            <button @click="store.logout(); mobileMenu = false; router.push('/')" class="block w-full text-left px-4 py-3 text-sm text-crypto-300 hover:bg-crypto-700/50 rounded-lg mx-2 w-[calc(100%-16px)]">Sign Out</button>
          </template>
          <template v-else>
            <router-link to="/login" class="block px-4 py-3 text-sm text-crypto-300 hover:bg-crypto-700/50 rounded-lg mx-2" @click="mobileMenu = false">Sign In</router-link>
            <router-link to="/register" class="block px-4 py-3 text-sm text-crypto-300 hover:bg-crypto-700/50 rounded-lg mx-2" @click="mobileMenu = false">Sign Up</router-link>
          </template>
        </div>
      </div>

      <!-- Theme Panel Overlay -->
      <div v-if="showThemePanel" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4" @click.self="showThemePanel = false">
        <div class="w-full max-w-md">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-white font-bold text-lg">Choose Theme</h3>
            <button @click="showThemePanel = false" class="text-crypto-400 hover:text-white p-1">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
          <ThemeSwitcher />
        </div>
      </div>
    </div>
  </header>
</template>

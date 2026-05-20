<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'

const router = useRouter()
const route = useRoute()
const store = useCryptoStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await store.login(email.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch {
    error.value = 'Login failed. Check your email and password.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
    <div class="w-full max-w-sm card p-8">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-white">Welcome Back</h1>
        <p class="text-crypto-400 text-sm mt-1">Sign in to your CryptoHub account</p>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Email</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="you@example.com"
            class="input-field w-full"
          />
        </div>
        <div>
          <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            required
            placeholder="Your password"
            class="input-field w-full"
          />
        </div>

        <div class="flex justify-end -mt-2">
          <router-link to="/forgot-password" class="text-xs text-crypto-400 hover:text-accent transition-colors">
            Forgot password?
          </router-link>
        </div>

        <p v-if="error" class="text-hot text-sm text-center">{{ error }}</p>

        <button type="submit" :disabled="loading" class="btn-primary w-full">
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
      </form>

      <p class="text-center text-sm text-crypto-400 mt-4">
        Don't have an account?
        <router-link :to="'/register' + (route.query.redirect ? '?redirect=' + route.query.redirect : '')" class="text-accent hover:underline">
          Create one
        </router-link>
      </p>
    </div>
  </div>
</template>

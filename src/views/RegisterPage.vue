<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCryptoStore } from '@/stores/crypto'

const router = useRouter()
const route = useRoute()
const store = useCryptoStore()

const email = ref('')
const name = ref('')
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  if (password.value !== confirm.value) {
    error.value = 'Passwords do not match.'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters.'
    return
  }
  loading.value = true
  try {
    await store.register(email.value, name.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch {
    error.value = 'Registration failed. The email may already be in use.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
    <div class="w-full max-w-sm card p-8">
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-white">Create Account</h1>
        <p class="text-crypto-400 text-sm mt-1">Join CryptoHub today</p>
      </div>

      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Name</label>
          <input
            v-model="name"
            type="text"
            required
            placeholder="Your name"
            class="input-field w-full"
          />
        </div>
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
            placeholder="At least 6 characters"
            class="input-field w-full"
          />
        </div>
        <div>
          <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Confirm Password</label>
          <input
            v-model="confirm"
            type="password"
            required
            placeholder="Repeat your password"
            class="input-field w-full"
          />
        </div>

        <p v-if="error" class="text-hot text-sm text-center">{{ error }}</p>

        <button type="submit" :disabled="loading" class="btn-primary w-full">
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>

      <p class="text-center text-sm text-crypto-400 mt-4">
        Already have an account?
        <router-link :to="'/login' + (route.query.redirect ? '?redirect=' + route.query.redirect : '')" class="text-accent hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>

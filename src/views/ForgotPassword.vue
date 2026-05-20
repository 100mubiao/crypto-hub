<script setup lang="ts">
import { ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const email = ref('')
const loading = ref(false)
const sent = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/forgot-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value }),
    })
    if (!res.ok) {
      const data = await res.json()
      error.value = data.detail || 'Something went wrong'
      return
    }
    sent.value = true
  } catch {
    error.value = 'Network error. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-[calc(100vh-8rem)] flex items-center justify-center px-4">
    <div class="w-full max-w-sm card p-8">
      <div v-if="sent" class="text-center">
        <div class="text-4xl mb-3">✉️</div>
        <h1 class="text-2xl font-bold text-white mb-2">Check Your Email</h1>
        <p class="text-crypto-400 text-sm leading-relaxed">
          If an account exists for <strong class="text-white">{{ email }}</strong>,
          we've sent a password reset link. It expires in 1 hour.
        </p>
        <router-link to="/login" class="btn-primary inline-block mt-6">Back to Login</router-link>
      </div>

      <template v-else>
        <div class="text-center mb-6">
          <h1 class="text-2xl font-bold text-white">Forgot Password</h1>
          <p class="text-crypto-400 text-sm mt-1">Enter your email and we'll send a reset link</p>
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

          <p v-if="error" class="text-hot text-sm text-center">{{ error }}</p>

          <button type="submit" :disabled="loading" class="btn-primary w-full">
            {{ loading ? 'Sending...' : 'Send Reset Link' }}
          </button>
        </form>

        <p class="text-center text-sm text-crypto-400 mt-4">
          Remember your password?
          <router-link to="/login" class="text-accent hover:underline">Sign in</router-link>
        </p>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const token = ref('')
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const done = ref(false)
const error = ref('')

onMounted(() => {
  token.value = (route.query.token as string) || ''
  if (!token.value) {
    error.value = 'Invalid reset link. No token found.'
  }
})

async function submit() {
  error.value = ''
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters.'
    return
  }
  if (password.value !== confirm.value) {
    error.value = 'Passwords do not match.'
    return
  }

  loading.value = true
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/reset-password`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: token.value, password: password.value }),
    })
    if (!res.ok) {
      const data = await res.json()
      error.value = data.detail || 'Reset failed. The link may have expired.'
      return
    }
    done.value = true
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
      <div v-if="done" class="text-center">
        <div class="text-4xl mb-3">✅</div>
        <h1 class="text-2xl font-bold text-white mb-2">Password Reset</h1>
        <p class="text-crypto-400 text-sm">Your password has been updated successfully.</p>
        <router-link to="/login" class="btn-primary inline-block mt-6">Sign In</router-link>
      </div>

      <template v-else>
        <div class="text-center mb-6">
          <h1 class="text-2xl font-bold text-white">Set New Password</h1>
          <p class="text-crypto-400 text-sm mt-1">Choose a strong password for your account</p>
        </div>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">New Password</label>
            <input
              v-model="password"
              type="password"
              required
              minlength="6"
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

          <button type="submit" :disabled="loading || !token" class="btn-primary w-full">
            {{ loading ? 'Resetting...' : 'Reset Password' }}
          </button>
        </form>
      </template>
    </div>
  </div>
</template>

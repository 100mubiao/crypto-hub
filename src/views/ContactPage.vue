<script setup lang="ts">
import { ref } from 'vue'

const name = ref('')
const email = ref('')
const message = ref('')
const sent = ref(false)

function submit() {
  if (!name.value || !email.value || !message.value) return
  sent.value = true
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 py-8">
    <h1 class="text-3xl sm:text-4xl font-bold text-white mb-2">Contact Us</h1>
    <p class="text-crypto-400 text-sm mb-10">Have a question, suggestion, or issue? We'd love to hear from you.</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <div>
        <div v-if="sent" class="card border-accent/30 text-center py-8">
          <div class="text-4xl mb-2">&#9993;</div>
          <h2 class="text-lg font-bold text-white mb-1">Message Sent!</h2>
          <p class="text-crypto-400 text-sm">We'll get back to you within 24 hours.</p>
        </div>

        <form v-else @submit.prevent="submit" class="space-y-5">
          <div>
            <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Name</label>
            <input v-model="name" type="text" required placeholder="Your name" class="input-field w-full" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Email</label>
            <input v-model="email" type="email" required placeholder="you@example.com" class="input-field w-full" />
          </div>
          <div>
            <label class="block text-xs uppercase tracking-wide text-crypto-400 mb-1">Message</label>
            <textarea v-model="message" required rows="5" placeholder="How can we help?" class="input-field w-full resize-none"></textarea>
          </div>
          <button type="submit" class="btn-primary w-full">Send Message</button>
        </form>
      </div>

      <div class="space-y-6">
        <div class="card">
          <h3 class="text-white font-bold mb-2">Email</h3>
          <p class="text-crypto-300 text-sm">support@cryptohub.dev</p>
          <p class="text-crypto-400 text-xs mt-1">We respond within 24 hours on business days.</p>
        </div>
        <div class="card">
          <h3 class="text-white font-bold mb-2">GitHub</h3>
          <p class="text-crypto-300 text-sm">github.com/cryptohub</p>
          <p class="text-crypto-400 text-xs mt-1">Open issues and feature requests are welcome.</p>
        </div>
        <div class="card">
          <h3 class="text-white font-bold mb-2">Community</h3>
          <p class="text-crypto-300 text-sm">Discord: discord.gg/cryptohub</p>
          <p class="text-crypto-400 text-xs mt-1">Join our community for real-time discussion and support.</p>
        </div>
        <div class="card border-hot/20">
          <h3 class="text-hot font-bold mb-2">Report Abuse</h3>
          <p class="text-crypto-300 text-sm">abuse@cryptohub.dev</p>
          <p class="text-crypto-400 text-xs mt-1">For reporting fraudulent or suspicious activity on the platform.</p>
        </div>
      </div>
    </div>
  </div>
</template>

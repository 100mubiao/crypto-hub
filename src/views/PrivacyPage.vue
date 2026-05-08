<script setup lang="ts">
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 py-8">
    <h1 class="text-3xl sm:text-4xl font-bold text-white mb-2">Privacy Policy</h1>
    <p class="text-crypto-400 text-sm mb-2">Last updated: May 8, 2026</p>
    <p class="text-crypto-400 text-sm mb-10">This Privacy Policy explains how CryptoHub collects, uses, and protects your information.</p>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">1. Information We Collect</h2>
      <p class="text-crypto-300 leading-relaxed mb-3">
        When you create an account on CryptoHub, we collect the following information:
      </p>
      <ul class="list-disc list-inside text-crypto-300 space-y-1 text-sm">
        <li>Email address</li>
        <li>Display name</li>
        <li>Account password (stored encrypted using bcrypt)</li>
        <li>Payment information is processed by third-party providers and is not stored on our servers</li>
      </ul>
      <p class="text-crypto-300 leading-relaxed mt-3">
        We also automatically collect anonymous usage data such as page views, feature interactions,
        and session duration to help us improve the platform.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">2. How We Use Your Information</h2>
      <ul class="list-disc list-inside text-crypto-300 space-y-1 text-sm">
        <li>To provide and maintain your account and membership status</li>
        <li>To send important service-related notifications (e.g., membership expiry, security alerts)</li>
        <li>To improve and optimize the platform based on usage patterns</li>
        <li>To respond to support inquiries and abuse reports</li>
      </ul>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">3. Data Sharing</h2>
      <p class="text-crypto-300 leading-relaxed">
        We do not sell, trade, or rent your personal information to third parties.
        We may share anonymized, aggregated data for analytical purposes.
        We will disclose information if required by law or to protect our legal rights.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">4. Data Security</h2>
      <p class="text-crypto-300 leading-relaxed">
        We implement industry-standard security measures including encrypted password storage (bcrypt),
        JWT-based session management, and HTTPS for all data transmission.
        However, no method of electronic storage is 100% secure, and we cannot guarantee absolute security.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">5. Your Rights</h2>
      <p class="text-crypto-300 leading-relaxed mb-3">
        You have the right to:
      </p>
      <ul class="list-disc list-inside text-crypto-300 space-y-1 text-sm">
        <li>Access the personal data we hold about you</li>
        <li>Request correction of inaccurate data</li>
        <li>Request deletion of your account and associated data</li>
        <li>Withdraw consent for data processing at any time</li>
        <li>Export your data in a machine-readable format</li>
      </ul>
      <p class="text-crypto-300 leading-relaxed mt-3">
        To exercise any of these rights, contact us at privacy@cryptohub.dev.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">6. Cookies</h2>
      <p class="text-crypto-300 leading-relaxed">
        CryptoHub uses essential cookies for authentication and session management.
        We do not use tracking cookies or third-party advertising cookies.
        You can control cookie settings through your browser preferences at any time.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">7. Third-Party Services</h2>
      <p class="text-crypto-300 leading-relaxed">
        We may use third-party services for payment processing and data infrastructure.
        These providers have their own privacy policies governing the use of your data.
        We only work with providers that maintain adequate security standards.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">8. Changes to This Policy</h2>
      <p class="text-crypto-300 leading-relaxed">
        We may update this Privacy Policy from time to time. We will notify users of material
        changes via email or through a notice on the platform. Continued use of CryptoHub
        after changes constitutes acceptance of the updated policy.
      </p>
    </section>

    <section class="mb-8">
      <h2 class="text-lg font-bold text-white mb-3">9. Contact</h2>
      <p class="text-crypto-300 leading-relaxed">
        If you have questions about this Privacy Policy, please contact us at privacy@cryptohub.dev
        or visit our <router-link to="/contact" class="text-accent hover:underline">Contact page</router-link>.
      </p>
    </section>
  </div>
</template>

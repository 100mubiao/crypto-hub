import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomePage.vue'),
  },
  {
    path: '/coin/:id',
    name: 'coin-detail',
    component: () => import('@/views/CoinDetail.vue'),
  },
  {
    path: '/trends',
    name: 'trends',
    component: () => import('@/views/TrendsPage.vue'),
  },
  {
    path: '/advanced-filter',
    name: 'advanced-filter',
    component: () => import('@/views/AdvancedFilter.vue'),
  },
  {
    path: '/pricing',
    name: 'pricing',
    component: () => import('@/views/PricingPage.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginPage.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterPage.vue'),
  },
  {
    path: '/checkout/success',
    name: 'checkout-success',
    component: () => import('@/views/CheckoutPage.vue'),
  },
  {
    path: '/checkout/:plan',
    name: 'checkout',
    component: () => import('@/views/CheckoutPage.vue'),
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutPage.vue'),
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/ContactPage.vue'),
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: () => import('@/views/PrivacyPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router

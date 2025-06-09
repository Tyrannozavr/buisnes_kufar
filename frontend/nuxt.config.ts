// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/icon',
    '@nuxt/image',
    '@nuxt/scripts',
    '@nuxt/test-utils',
    '@pinia/nuxt',
    'pinia-plugin-persistedstate/nuxt',
  ],
  css: ['~/assets/css/main.css'],

  future: {
    compatibilityVersion: 4
  },
  runtimeConfig: {
    // Private keys that are exposed to the server

    // Keys within public are also exposed to the client
    public: {
      apiBaseUrl: process.env.NUXT_API_URL || 'http://localhost:3000/api'
    }
  },
  // Add explicit colorMode configuration
  ui: {
    colorMode: false
  },
  compatibilityDate: '2024-11-27',
  ssr: true
})
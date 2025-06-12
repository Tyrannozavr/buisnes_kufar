
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    'pinia-plugin-persistedstate/nuxt',
    '@nuxt/image'
  ],
  css: ['~/assets/css/tailwind.css'],
  future: {
    compatibilityVersion: 4
  },
  runtimeConfig: {
    // Private keys that are exposed to the server

    // Keys within public are also exposed to the client
    public: {
      apiBaseUrl: process.env.VITE_PUBLIC_API_URL || 'http://localhost:3000/api'
    }
  },
  // Add explicit colorMode configuration
  ui: {
    colorMode: false,
  },
  compatibilityDate: '2024-11-27',
  ssr: true,
  colorMode: {
    classSuffix: ''
  },
  app: {
    head: {
      title: 'БизнесТорг',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'БизнесТорг - платформа для бизнеса' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  }
})
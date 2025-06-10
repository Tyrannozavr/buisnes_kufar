// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    '@nuxt/ui',
    'pinia-plugin-persistedstate/nuxt',
    '@nuxt/image'
  ],
  css: ['~/assets/css/main.css'],

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
    global: true,
    icons: ['heroicons']
  },
  compatibilityDate: '2024-11-27',
  ssr: true,
  i18n: {
    vueI18n: './i18n.config.ts',
    strategy: 'no_prefix',
    defaultLocale: 'ru',
    detectBrowserLanguage: false
  },
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
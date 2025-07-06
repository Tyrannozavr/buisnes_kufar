// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },

  modules: [
    '@nuxt/ui',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    'pinia-plugin-persistedstate/nuxt',
    '@nuxt/image',
    '@nuxt/icon'
  ],
  css: ['~/assets/css/main.css'],
  future: {
    compatibilityVersion: 4
  },
  runtimeConfig: {
    // Private keys that are exposed to the server

    // Keys within public are also exposed to the client
    public: {
      apiBaseUrl: process.env.VITE_PUBLIC_API_URL || '/api'
    }
  },
  // Отключаем загрузку шрифтов через переменную окружения
  nitro: {
    experimental: {
      wasm: true
    }
  },
  // Add explicit colorMode configuration
  ui: {
    colorMode: false,
    // Полностью отключаем автоматическую загрузку шрифтов
    fonts: false
  },
  // Configure Nuxt Icon
  icon: {
    size: '24px',
    class: 'icon',
    aliases: {
      'nuxt': 'logos:nuxt-icon',
    }
  },
  compatibilityDate: '2024-11-27',
  ssr: true,
  colorMode: {
    preference: 'light', // принудительно использует только светлую тему
    fallback: 'light',   // если preference не указан, всё равно будет светлая
    classSuffix: ''      // убирает суффиксы классов (например 'light:')
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
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
    apiBaseUrl: process.env.API_BASE_URL,
    
    // Keys within public are also exposed to the client
    public: {
      apiBaseUrl: process.env.VITE_PUBLIC_API_URL
    }
  },
  // Настройки для работы через nginx
  nitro: {
    experimental: {
      wasm: true
    },
    // Указываем правильный baseURL для статических ресурсов
    baseURL: '/',
    // Настройки для правильной работы с API в production
    routeRules: {
      '/api/**': { 
        headers: { 'cache-control': 's-maxage=60' },
        cors: true
      }
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
    provider: 'server',
    serverBundle: {
      collections: ['heroicons', 'lucide', 'simple-icons']
    },
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
    baseURL: '/',
    head: {
      title: 'TradeSynergy',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'TradeSynergy - платформа для бизнеса' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },
  // Настройки для работы в dev режиме через nginx
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },
  // Настройки для правильной генерации путей
  vite: {
    // Proxy для dev режима - проксируем /api запросы на backend
    server: {
      proxy: {
        // Исключаем _nuxt_icon из прокси
        '^/api/(?!_nuxt_icon)': {
          // Dev proxy target берём из .env, чтобы менять в одном месте.
          // В docker обычно: http://backend:8000
          // При запуске фронта на хосте: http://localhost:8002
          target: process.env.NUXT_DEV_API_PROXY_TARGET || 'http://backend:8000',
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path
        }
      }
    }
  },
  // Конфигурация PostCSS
  postcss: {
    plugins: {
      '@tailwindcss/postcss': {},
      autoprefixer: {},
    }
  }
})
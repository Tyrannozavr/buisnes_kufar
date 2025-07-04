export default defineAppConfig({
  // https://ui.nuxt.com/getting-started/theme#design-system
  ui: {
    colors: {
      primary: 'emerald',
      neutral: 'slate',
    },
    button: {
      defaultVariants: {
        // Set default button color to neutral
        // color: 'neutral'
      }
    },
    // Add dark mode configuration
    strategy: 'class',
    // Отключаем автоматическую загрузку шрифтов
    fonts: {
      families: {
        sans: false
      }
    }
  }
})

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
    // Выпадающие списки по умолчанию равны ширине триггера (часто узкий inline).
    // min-w гарантирует читаемые пункты даже в узких колонках сетки.
    selectMenu: {
      slots: {
        base: 'w-full min-w-0',
        content: 'min-w-56 max-w-[min(100vw-2rem,28rem)]',
        itemLabel: 'whitespace-normal break-words',
      },
    },
    select: {
      slots: {
        base: 'w-full min-w-0',
        content: 'min-w-56 max-w-[min(100vw-2rem,28rem)]',
        itemLabel: 'whitespace-normal break-words',
      },
    },
    // Add dark mode configuration
    strategy: 'class',
    // Полностью отключаем автоматическую загрузку шрифтов
    fonts: false
  }
})

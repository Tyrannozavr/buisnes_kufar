export default defineNuxtPlugin(() => {
  // В dev (и вообще локально) часто остаётся сохранённый "dark" в localStorage от @nuxtjs/color-mode.
  // Прод у вас уже принудительно светлый, делаем то же самое и в разработке.
  try {
    // Ключ по умолчанию у @nuxtjs/color-mode
    localStorage.setItem('nuxt-color-mode', 'light')
    localStorage.setItem('color-mode', 'light')
  } catch {
    // ignore
  }

  // На всякий случай убираем классы dark и принудительно ставим light
  document.documentElement.classList.remove('dark')
  document.documentElement.classList.add('light')
})


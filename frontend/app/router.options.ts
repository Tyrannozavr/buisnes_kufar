import type { RouterConfig } from '@nuxt/schema'

export default <RouterConfig>{
  scrollBehavior(to, from, savedPosition) {
    // При смене только hash (вкладки Заказ / Счет / Договор поставки и т.д.) не прокручивать — оставаться на том же уровне
    if (from && to.path === from.path && to.hash) {
      return false
    }
    return savedPosition ?? { top: 0, left: 0 }
  },
}

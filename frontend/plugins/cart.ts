import { useCartStore } from '~/stores/cart'

export default defineNuxtPlugin(() => {
  const cartStore = useCartStore()
  
  // Инициализируем корзину при загрузке приложения
  if (process.client) {
    cartStore.init()
  }
}) 
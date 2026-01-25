import { ref } from 'vue'
import { useCartStore } from '~/stores/cart'
import { useUserStore } from '~/stores/user'
import type {Product, ProductItemPublic} from '~/types/product'

const cart = ref<Map<string, number>>(new Map())

export const useCart = () => {
  const cartStore = useCartStore()
  const userStore = useUserStore()
  const toast = useToast()

  const handleAddToCart = async (product: ProductItemPublic) => {
    if (!userStore.isAuthenticated) {
      toast.add({
        title: 'Требуется авторизация',
        description: 'Пожалуйста, войдите в систему, чтобы добавить товар в корзину',
        color: 'warning'
      })
      return
    }

    try {
      cartStore.addToCart(product)
      toast.add({
        title: 'Успешно',
        description: 'Товар добавлен в корзину',
        color: 'success'
      })
    } catch (error) {
      toast.add({
        title: 'Ошибка',
        description: 'Не удалось добавить товар в корзину',
        color: 'error'
      })
    }
  }

  const handleIncreaseQuantity = (productSlug: string, currentQuantity: number) => {
    cartStore.updateQuantity(productSlug, currentQuantity + 1)
  }

  const handleDecreaseQuantity = (productSlug: string, currentQuantity: number) => {
    if (currentQuantity > 1) {
      cartStore.updateQuantity(productSlug, currentQuantity - 1)
    } else {
      cartStore.removeFromCart(productSlug)
    }
  }

  const updateQuantity = (productSlug: string, newQuantity: number) => {
    if (newQuantity > 0) {
      cartStore.updateQuantity(productSlug, newQuantity)
    } else {
      cartStore.removeFromCart(productSlug)
    }
  }

  const getQuantity = (productSlug: string) => {
    const item = cartStore.items.find(item => item.product.slug === productSlug)
    return item?.quantity ?? 0
  }

  return {
    handleAddToCart,
    handleIncreaseQuantity,
    handleDecreaseQuantity,
    updateQuantity,
    getQuantity
  }
} 
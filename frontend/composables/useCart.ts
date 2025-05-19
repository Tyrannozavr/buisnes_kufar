import { useCartStore } from '~/stores/cart'
import { useUserStore } from '~/stores/user'
import type { Product } from '~/types/product'

export const useCart = () => {
  const cartStore = useCartStore()
  const userStore = useUserStore()
  const toast = useToast()

  const handleAddToCart = async (product: Product) => {
    if (!userStore.isAuthenticated) {
      toast.add({
        title: 'Требуется авторизация',
        description: 'Пожалуйста, войдите в систему, чтобы добавить товар в корзину',
        color: 'warning'
      })
      return
    }

    try {
      await cartStore.addToCart(product)
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

  const handleIncreaseQuantity = (productId: string, currentQuantity: number) => {
    cartStore.updateQuantity(productId, currentQuantity + 1)
  }

  const handleDecreaseQuantity = (productId: string, currentQuantity: number) => {
    if (currentQuantity > 1) {
      cartStore.updateQuantity(productId, currentQuantity - 1)
    } else {
      cartStore.removeFromCart(productId)
    }
  }

  const getQuantity = (productId: string) => {
    const item = cartStore.items.find(item => item.product.id === productId)
    return item?.quantity ?? 0
  }

  return {
    handleAddToCart,
    handleIncreaseQuantity,
    handleDecreaseQuantity,
    getQuantity
  }
} 
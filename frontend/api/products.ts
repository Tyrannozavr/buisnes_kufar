import type { Product } from '~/types/product'

export const useProductsApi = () => {
  const { data: products, refresh } = useApi<Product[]>('/products')

  const searchProducts = async (params: {
    name?: string
    country?: string
    federalDistrict?: string
    region?: string
    city?: string
  } = {}) => {
    return useApi<Product[]>('/products', {
      query: params
    })
  }

  const hideProduct = async (productId: string) => {
    try {
      await useApi(`/products/${productId}/hide`, {
        method: 'PUT'
      })
      await refresh()
      useToast().add({
        title: 'Успешно',
        description: 'Продукт скрыт',
        color: 'success'
      })
    } catch {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось скрыть продукт',
        color: 'error'
      })
    }
  }

  const deleteProduct = async (productId: string) => {
    try {
      await useApi(`/products/${productId}/delete`, {
        method: 'PUT'
      })
      await refresh()
      useToast().add({
        title: 'Успешно',
        description: 'Продукт удален',
        color: 'success'
      })
    } catch {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось удалить продукт',
        color: 'error'
      })
    }
  }

  const restoreProduct = async (productId: string) => {
    try {
      await useApi(`/products/${productId}/restore`, {
        method: 'PUT'
      })
      await refresh()
      useToast().add({
        title: 'Успешно',
        description: 'Продукт восстановлен',
        color: 'success'
      })
    } catch {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось восстановить продукт',
        color: 'error'
      })
    }
  }

  const saveProduct = async (productData: Partial<Product>, productId?: string) => {
    try {
      if (productId) {
        await useApi(`/products/${productId}`, {
          method: 'PUT',
          body: productData
        })
        useToast().add({
          title: 'Успешно',
          description: 'Продукт обновлен',
          color: 'success'
        })
      } else {
        await useApi('/products', {
          method: 'POST',
          body: productData
        })
        useToast().add({
          title: 'Успешно',
          description: 'Продукт добавлен',
          color: 'success'
        })
      }
      await refresh()
      return true
    } catch {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось сохранить продукт',
        color: 'error'
      })
      return false
    }
  }

  return {
    products,
    refresh,
    searchProducts,
    hideProduct,
    deleteProduct,
    restoreProduct,
    saveProduct
  }
} 
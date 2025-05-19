import type { Product, ProductResponse } from '~/types/product'
import type { Service, ServiceResponse } from '~/types/service'
import { useApi } from '~/composables/useApi'

export const useProductsApi = () => {
  const getProducts = async (params?: { page?: number; perPage?: number; limit?: number }) => {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.perPage) queryParams.append('perPage', params.perPage.toString())
    if (params?.limit) queryParams.append('limit', params.limit.toString())

    const query = queryParams.toString() ? `?${queryParams.toString()}` : ''
    return await useApi<ProductResponse>(`/products${query}`)
  }

  const getProduct = async (id: string) => {
    return await useApi<Product>(`/products/${id}`)
  }

  const searchProducts = async (params: {
    name?: string
    country?: string
    federalDistrict?: string
    region?: string
    city?: string
  } = {}) => {
    return useApi<ProductResponse>('/products', {
      query: params
    })
  }

  const searchServices = async (params: {
    name?: string
    country?: string
    federalDistrict?: string
    region?: string
    city?: string
  } = {}) => {
    return useApi<ServiceResponse>('/services', {
      query: params
    })
  }

  const hideProduct = async (productId: string) => {
    try {
      await useApi(`/products/${productId}/hide`, {
        method: 'PUT'
      })
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
    getProducts,
    getProduct,
    searchProducts,
    searchServices,
    hideProduct,
    deleteProduct,
    restoreProduct,
    saveProduct
  }
} 
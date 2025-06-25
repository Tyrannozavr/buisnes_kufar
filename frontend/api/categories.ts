import type { Category } from '~/types/category'
import type { UseFetchOptions } from 'nuxt/app'

export const useCategoriesApi = () => {
  const getCategories = (options: UseFetchOptions<Category[]> = {}) => {
    return useApi<Category[]>('/v1/company/announcements/categories', {
      ...options
    })
  }

  return {
    getCategories
  }
} 
import type { Company, CompanyStatistics } from '~/types/company'
import type { Product } from '~/types/product'
import type { Review } from '~/types/review'
import type { UseFetchOptions } from 'nuxt/app'
import { useRuntimeConfig, useCookie } from 'nuxt/app'

export const getMyCompany = async () => {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  const accessToken = useCookie('access_token')

  try {
    const headers = new Headers({
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    })
    
    if (accessToken.value) {
      headers.set('Authorization', `Bearer ${accessToken.value}`)
    }

    const response = await $fetch<Company>(`${apiBaseUrl}/v1/company/me`, {
      credentials: 'include',
      headers
    })
    return response
  } catch (error: any) {
    throw error
  }
}

export const updateCompany = (data: Partial<Company>, options: UseFetchOptions<Company> = {}) => {
  return useApi<Company>('/company/me', {
    method: 'PUT',
    body: data,
    ...options
  })
}

export const getCompany = async (id: string) => {
  return await useApi<Company>(`/companies/${id}`)
}

export const getCompanyProducts = (options: UseFetchOptions<Product[]> = {}) => {
  return useApi<Product[]>('/company/products', options)
}
export const getMyProducts = (options: UseFetchOptions<Product[]> = {}) => {
  return useApi<{data: Product[]}>('/products', options)
}

export const getCompanyReviews = async (id: string) => {
  return await useApi<Review[]>(`/companies/${id}/reviews`)
}

export const getCompanyStatistics = async (id: string) => {
  return await useApi<CompanyStatistics>(`/companies/${id}/statistics`)
} 
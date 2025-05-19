import type { Company, CompanyStatistics } from '~/types/company'
import type { Product } from '~/types/product'
import type { Review } from '~/types/review'
import type { UseFetchOptions } from 'nuxt/app'

export const getMyCompany = (options: UseFetchOptions<Company> = {}) => {
  return useApi<Company>('/company/me', options)
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

export const getCompanyProducts = async (id: string) => {
  return await useApi<Product[]>(`/companies/${id}/products`)
}

export const getCompanyReviews = async (id: string) => {
  return await useApi<Review[]>(`/companies/${id}/reviews`)
}

export const getCompanyStatistics = async (id: string) => {
  return await useApi<CompanyStatistics>(`/companies/${id}/statistics`)
} 
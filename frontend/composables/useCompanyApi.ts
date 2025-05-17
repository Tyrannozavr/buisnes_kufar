import type { Company, CompanyDetails, CompanyStatistics } from '~/types/company'
import type { Product } from '~/types/product'
import type { Review } from '~/types/review'

export const useCompanyApi = () => {
  const getCompany = async (id: string) => {
    return await useApi<Company>(`/companies/${id}`)
  }

  const getCompanyProducts = async (id: string) => {
    return await useApi<Product[]>(`/companies/${id}/products`)
  }

  const getCompanyReviews = async (id: string) => {
    return await useApi<Review[]>(`/companies/${id}/reviews`)
  }

  const getCompanyStatistics = async (id: string) => {
    return await useApi<CompanyStatistics>(`/companies/${id}/statistics`)
  }

  return {
    getCompany,
    getCompanyProducts,
    getCompanyReviews,
    getCompanyStatistics
  }
} 
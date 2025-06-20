import type { CompanyResponse, CompanyStatistics } from '~/types/company'
import type {UseFetchOptions} from "nuxt/app";
import type { CompanyProducts } from "~/components/company/CompanyProducts.vue";

export const getCompanyStatistics = async (slug: string): Promise<{ data: CompanyStatistics }> => {
  // В реальном приложении здесь был бы API-запрос
  return {
    data: {
      totalViews: 0,
      monthlyViews: 0,
      totalPurchases: 0,
      // Добавьте другие статистические поля, если они есть в CompanyStatisticsResponse
    }
  }
}

export const getCompanyProducts = async (slug: string): Promise<{ data: CompanyStatistics }> => {
  // В реальном приложении здесь был бы API-запрос
  return useApi<CompanyProducts>(`/v1/companies/slug/${slug}`, {
    method: 'GET',
    ...options
  })
}

export const getCompany = async (slug: string, options: UseFetchOptions<void> = {}): Promise<{ data: CompanyResponse }> => {
  return useApi<CompanyResponse>(`/v1/companies/slug/${slug}`, {
    method: 'GET',
    ...options
  })
}
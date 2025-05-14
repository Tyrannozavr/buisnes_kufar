import type { Company } from '~/types/company'
import type { UseFetchOptions } from 'nuxt/app'

export const useCompaniesApi = () => {
  const getCompanies = (options: UseFetchOptions<Company[]> = {}) => {
    return useApi<Company[]>('/companies', {
      transform: (data) =>
        data.sort((a, b) => new Date(b.registrationDate).getTime() - new Date(a.registrationDate).getTime()),
      ...options
    })
  }

  const getLatestCompanies = (limit: number = 5, options: UseFetchOptions<Company[]> = {}) => {
    return useApi<Company[]>('/companies', {
      transform: (data) =>
        data
          .sort((a, b) => new Date(b.registrationDate).getTime() - new Date(a.registrationDate).getTime())
          .slice(0, limit),
      ...options
    })
  }

  return {
    getCompanies,
    getLatestCompanies
  }
} 
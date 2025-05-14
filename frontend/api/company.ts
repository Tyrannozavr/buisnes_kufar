import type { Company } from '~/types/company'
import type { UseFetchOptions } from 'nuxt/app'

export const useCompanyApi = () => {
  const getMyCompany = (options: UseFetchOptions<Company> = {}) => {
    return useApi<Company>('/company/me', options)
  }

  const updateCompany = (data: Partial<Company>, options: UseFetchOptions<Company> = {}) => {
    return useApi<Company>('/company/me', {
      method: 'PUT',
      body: data,
      ...options
    })
  }

  return {
    getMyCompany,
    updateCompany
  }
} 
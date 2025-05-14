import type { PartnerCompany } from '~/types/company'
import type { UseFetchOptions } from 'nuxt/app'

export const useBuyersApi = () => {
  const getBuyers = (options: UseFetchOptions<PartnerCompany[]> = {}) => {
    return useApi<PartnerCompany[]>('/company/buyers', options)
  }

  const removeBuyer = (slug: string, options: UseFetchOptions<void> = {}) => {
    return useApi<void>(`/company/buyers/${slug}`, {
      method: 'DELETE',
      ...options
    })
  }

  return {
    getBuyers,
    removeBuyer
  }
} 
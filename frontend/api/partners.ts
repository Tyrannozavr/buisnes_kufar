import type { PartnerCompany } from '~/types/company'
import type { UseFetchOptions } from 'nuxt/app'

export const usePartnersApi = () => {
  const getPartners = (options: UseFetchOptions<PartnerCompany[]> = {}) => {
    return useApi<PartnerCompany[]>('/company/partners', options)
  }

  const removePartner = (slug: string, options: UseFetchOptions<void> = {}) => {
    return useApi<void>(`/company/partners/${slug}`, {
      method: 'DELETE',
      ...options
    })
  }

  return {
    getPartners,
    removePartner
  }
} 
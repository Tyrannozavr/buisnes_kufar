import type { PartnerCompany } from '~/types/company'
import type { UseFetchOptions } from 'nuxt/app'

export const useSuppliersApi = () => {
  const getSuppliers = (options: UseFetchOptions<PartnerCompany[]> = {}) => {
    return useApi<PartnerCompany[]>('/company/suppliers', options)
  }

  const removeSupplier = (slug: string, options: UseFetchOptions<void> = {}) => {
    return useApi<void>(`/company/suppliers/${slug}`, {
      method: 'DELETE',
      ...options
    })
  }

  return {
    getSuppliers,
    removeSupplier
  }
} 
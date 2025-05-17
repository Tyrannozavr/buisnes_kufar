import type { Company } from '~/types/company'

export interface ManufacturersSearchParams {
  search?: string
  country?: string
  federalDistrict?: string
  region?: string
  city?: string
  product?: string
}

export const useManufacturersApi = () => {
  const searchManufacturers = async (params: ManufacturersSearchParams) => {
    return await useApi<Company[]>('/manufacturers', {
      query: params
    })
  }

  return {
    searchManufacturers
  }
} 
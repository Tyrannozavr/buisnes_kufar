import type { FilterItem } from '~/types/filters'

export interface ProductFiltersResponse {
  countries: FilterItem[]
  federal_districts: FilterItem[]
  regions: FilterItem[]
  cities: FilterItem[]
}

export interface ServiceFiltersResponse {
  countries: FilterItem[]
  federal_districts: FilterItem[]
  regions: FilterItem[]
  cities: FilterItem[]
}

export interface CompanyFiltersResponse {
  countries: FilterItem[]
  federal_districts: FilterItem[]
  regions: FilterItem[]
  cities: FilterItem[]
}

export interface ProductFilterRequest {
  search?: string
  country?: string
  federal_district?: string
  region?: string
  city?: string
  min_price?: number
  max_price?: number
  in_stock?: boolean
  skip?: number
  limit?: number
}

export interface ServiceFilterRequest {
  search?: string
  country?: string
  federal_district?: string
  region?: string
  city?: string
  min_price?: number
  max_price?: number
  in_stock?: boolean
  skip?: number
  limit?: number
}

export const useProductFilters = () => {
  const { $api } = useNuxtApp()
  
  const getProductFilters = async (): Promise<ProductFiltersResponse> => {
    return await $api.get('/v1/products/filters')
  }
  
  const searchProducts = async (filters: ProductFilterRequest): Promise<any> => {
    return await $api.post('/v1/products/search', filters)
  }
  
  return {
    getProductFilters,
    searchProducts
  }
}

export const useServiceFilters = () => {
  const { $api } = useNuxtApp()
  
  const getServiceFilters = async (): Promise<ServiceFiltersResponse> => {
    return await $api.get('/v1/products/services/filters')
  }
  
  const searchServices = async (filters: ServiceFilterRequest): Promise<any> => {
    return await $api.post('/v1/products/services/search', filters)
  }
  
  return {
    getServiceFilters,
    searchServices
  }
}

export const useCompanyFilters = () => {
  const { $api } = useNuxtApp()
  
  const getCompanyFilters = async (): Promise<CompanyFiltersResponse> => {
    return await $api.get('/v1/company/filters')
  }
  
  return {
    getCompanyFilters
  }
} 
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
  
  const getCitiesByLocation = async (countryCode: string, regionCode?: string): Promise<FilterItem[]> => {
    const params = new URLSearchParams({ country_code: countryCode })
    if (regionCode) {
      params.append('region_code', regionCode)
    }
    const response = await $api.get(`/v1/locations/v2/cities?${params.toString()}`)
    return response.items || []
  }
  
  const getRegionsByCountry = async (countryCode: string): Promise<FilterItem[]> => {
    const response = await $api.get(`/v1/locations/v2/regions?country_code=${countryCode}`)
    return response.items || []
  }
  
  const getFederalDistrictsByCountry = async (countryCode: string): Promise<FilterItem[]> => {
    const response = await $api.get(`/v1/locations/v2/federal-districts?country_code=${countryCode}`)
    return response.items || []
  }
  
  const searchProducts = async (filters: ProductFilterRequest): Promise<any> => {
    return await $api.post('/v1/products/search', filters)
  }
  
  return {
    getProductFilters,
    getCitiesByLocation,
    getRegionsByCountry,
    getFederalDistrictsByCountry,
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
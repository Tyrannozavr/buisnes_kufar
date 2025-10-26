import type {Company, CompanyShort, ManufacturersSearchParams} from '~/types/company'
import type { PaginationResponse } from '~/types/api'
import { API_URLS } from '~/constants/urls'

export const useCompaniesApi = () => {
  const { $api } = useNuxtApp()

  const getCompanies = async (params: {
    page?: number
    perPage?: number
    limit?: number
  } = {}) => {
    const { page = 1, perPage = 10, limit } = params
    
    const queryParams: Record<string, any> = {
      page,
      perPage
    }
    
    if (limit) {
      queryParams.limit = limit
    }

    return await $api.get(API_URLS.COMPANIES, { params: queryParams })
  }

  const getCompaniesPaginated = async (page: number = 1, perPage: number = 10) => {
    return await $api.get(API_URLS.COMPANIES, {
      params: { page, perPage }
    }) as PaginationResponse<Company>
  }

  const getLatestCompanies = async (limit: number = 6) => {
    return await $api.get(API_URLS.COMPANIES, {
      params: { limit }
    }) as Company[]
  }

  const searchManufacturers = async (params: any = {}) => {
    return await $api.get('/v1/companies/products', { params })
  }

  const searchServiceProviders = async (params: any = {}) => {
    return await $api.get('/v1/companies/services', { params })
  }

  const deletePartnerById = async (id: string) => {
    return await $api.delete(`/companies/${id}`)
  }

  const getCompanyById = async (id: string | number, short: boolean = true) => {
    return await $api.get(`${API_URLS.COMPANIES}${id}`, {
      params: { short }
    }) as Company
  }

  return {
    getCompanies,
    getCompaniesPaginated,
    getLatestCompanies,
    searchManufacturers,
    searchServiceProviders,
    deletePartnerById,
    getCompanyById,
  }
}

// SSR-ready functions
export const getCompaniesSSR = async (params: {
  page?: number
  perPage?: number
  limit?: number
} = {}) => {
  const { $api } = useNuxtApp()
  const { page = 1, perPage = 10, limit } = params
  
  const queryParams: Record<string, any> = {
    page,
    perPage
  }
  
  if (limit) {
    queryParams.limit = limit
  }

  return await $api.get(API_URLS.COMPANIES, { params: queryParams })
}

export const getCompaniesPaginatedSSR = async (page: number = 1, perPage: number = 10) => {
  const { $api } = useNuxtApp()
  return await $api.get(API_URLS.COMPANIES, {
    params: { page, perPage }
  }) as PaginationResponse<Company>
}

export const getLatestCompaniesSSR = async (limit: number = 6) => {
  const { $api } = useNuxtApp()
  return await $api.get(API_URLS.COMPANIES, {
    params: { limit }
  }) as PaginationResponse<Company>
}

export const searchManufacturersSSR = async (page: number = 1, perPage: number = 10, params: any = {}) => {
  const queryParams: any = {
    page,
    per_page: perPage
  }
  
  // Добавляем параметры фильтрации
  if (params.search) queryParams.search = params.search
  if (params.cities && params.cities.length > 0) {
    queryParams.cities = params.cities.join(',')
  }
  
  // Используем $fetch для SSR
  const config = useRuntimeConfig()
  const url = `${config.public.apiBase || ''}/v1/companies/`
  
  return await $fetch(url, {
    query: queryParams
  }) as PaginationResponse<CompanyShort>
}

export const searchServiceProvidersSSR = async (page: number = 1, perPage: number = 10, params: any = {}) => {
  const queryParams: any = {
    page,
    per_page: perPage
  }
  
  // Добавляем параметры фильтрации
  if (params.search) queryParams.search = params.search
  if (params.cities && Array.isArray(params.cities) && params.cities.length > 0) {
    queryParams.cities = params.cities.join(',')
  }
  
  // Используем $fetch для SSR
  const config = useRuntimeConfig()
  const url = `${config.public.apiBase || ''}/v1/companies/services`
  
  return await $fetch(url, {
    query: queryParams
  }) as PaginationResponse<CompanyShort>
} 
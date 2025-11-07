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
    // Формируем body для POST запроса (как в products)
    const body: any = {
      search: params.search || undefined,
      cities: params.cities || undefined, // Массив ID городов
      skip: ((params.page || 1) - 1) * (params.perPage || 10),
      limit: params.perPage || 10
    }
    
    // Убираем undefined значения
    Object.keys(body).forEach(key => {
      if (body[key] === undefined || body[key] === null) {
        delete body[key]
      }
    })
    
    return await $api.post('/v1/companies/products/search', body)
  }

  const searchServiceProviders = async (params: any = {}) => {
    // Формируем body для POST запроса
    const body: any = {
      search: params.search || undefined,
      cities: params.cities || undefined,
      skip: ((params.page || 1) - 1) * (params.perPage || 10),
      limit: params.perPage || 10
    }
    
    // Убираем undefined значения
    Object.keys(body).forEach(key => {
      if (body[key] === undefined || body[key] === null) {
        delete body[key]
      }
    })
    
    return await $api.post('/v1/companies/services/search', body)
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
  // Формируем body для POST запроса (как в products)
  const body: any = {
    search: params.search || undefined,
    cities: params.cities || undefined,
    skip: (page - 1) * perPage,
    limit: perPage
  }
  
  // Убираем undefined значения
  Object.keys(body).forEach(key => {
    if (body[key] === undefined || body[key] === null) {
      delete body[key]
    }
  })
  
  // Используем $fetch для SSR с POST
  const config = useRuntimeConfig()
  const baseUrl = process.server ? (config.public.apiBase || 'http://localhost:8000/api') : '/api'
  const url = `${baseUrl}/v1/companies/products/search`
  
  return await $fetch(url, {
    method: 'POST',
    body
  }) as PaginationResponse<CompanyShort>
}

export const searchServiceProvidersSSR = async (page: number = 1, perPage: number = 10, params: any = {}) => {
  // Формируем body для POST запроса
  const body: any = {
    search: params.search || undefined,
    cities: params.cities || undefined,
    skip: (page - 1) * perPage,
    limit: perPage
  }
  
  // Убираем undefined значения
  Object.keys(body).forEach(key => {
    if (body[key] === undefined || body[key] === null) {
      delete body[key]
    }
  })
  
  // Используем $fetch для SSR с POST
  const config = useRuntimeConfig()
  const baseUrl = process.server ? (config.public.apiBase || 'http://localhost:8000/api') : '/api'
  const url = `${baseUrl}/v1/companies/services/search`
  
  return await $fetch(url, {
    method: 'POST',
    body
  }) as PaginationResponse<CompanyShort>
} 
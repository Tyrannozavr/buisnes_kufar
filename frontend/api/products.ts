import type { Product, ProductResponse, ProductListResponse } from '~/types/product'
import type { ProductSearchParams, ServiceSearchParams, ProductResponse as FilterProductResponse } from '~/types/filters'
import { useNuxtApp } from 'nuxt/app'


// URL-адреса API
const API_URLS = {
  BASE: '/v1/products',
  GOODS: '/v1/products/goods',
  SERVICES: '/v1/products/services',
  SEARCH: '/v1/products/search',
  LATEST: '/v1/products/latest',
  COMPANY: (companyId: string | number) => `/v1/products/company/${companyId}`,
  COMPANY_GOODS: (companyId: string | number) => `/v1/products/company/${companyId}/goods`,
  COMPANY_SERVICES: (companyId: string | number) => `/v1/products/company/${companyId}/services`,
  BY_ID: (id: string | number) => `/v1/products/${id}`,
  BY_SLUG: (companyId: string | number, slug: string) => `/v1/products/company/${companyId}/slug/${slug}`,
} as const

export const useProductsApi = () => {
  const { $api } = useNuxtApp()

  // Получить все товары
  const getAllGoods = async (params?: {
    skip?: number
    limit?: number
    include_hidden?: boolean
  }): Promise<ProductListResponse> => {
    const searchParams = new URLSearchParams()
    
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
    if (params?.include_hidden !== undefined) searchParams.append('include_hidden', params.include_hidden.toString())
    
    const query = searchParams.toString()
    const url = `${API_URLS.GOODS}${query ? `?${query}` : ''}`
    
    return await $api.get(url)
  }

  // Получить все услуги
  const getAllServices = async (params?: {
    skip?: number
    limit?: number
    include_hidden?: boolean
  }): Promise<ProductListResponse> => {
    const searchParams = new URLSearchParams()
    
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
    if (params?.include_hidden !== undefined) searchParams.append('include_hidden', params.include_hidden.toString())
    
    const query = searchParams.toString()
    const url = `${API_URLS.SERVICES}${query ? `?${query}` : ''}`
    
    return await $api.get(url)
  }

  // Поиск товаров
  const searchProducts = async (searchParams: ProductSearchParams): Promise<FilterProductResponse> => {
    const params = new URLSearchParams()
    
    if (searchParams.search) params.append('search', searchParams.search)
    if (searchParams.country) params.append('country', searchParams.country)
    if (searchParams.federalDistrict) params.append('federal_district', searchParams.federalDistrict)
    if (searchParams.region) params.append('region', searchParams.region)
    if (searchParams.city) params.append('city', searchParams.city)
    if (searchParams.type) params.append('type', searchParams.type)
    if (searchParams.minPrice !== undefined) params.append('min_price', searchParams.minPrice.toString())
    if (searchParams.maxPrice !== undefined) params.append('max_price', searchParams.maxPrice.toString())
    if (searchParams.inStock !== undefined) params.append('in_stock', searchParams.inStock.toString())
    
    const query = params.toString()
    const url = `${API_URLS.SEARCH}${query ? `?${query}` : ''}`
    
    return await $api.get(url)
  }

  // Поиск услуг
  const searchServices = async (searchParams: ServiceSearchParams): Promise<FilterProductResponse> => {
    const params = new URLSearchParams()
    
    if (searchParams.search) params.append('search', searchParams.search)
    if (searchParams.country) params.append('country', searchParams.country)
    if (searchParams.federalDistrict) params.append('federal_district', searchParams.federalDistrict)
    if (searchParams.region) params.append('region', searchParams.region)
    if (searchParams.city) params.append('city', searchParams.city)
    if (searchParams.type) params.append('type', searchParams.type)
    if (searchParams.minPrice !== undefined) params.append('min_price', searchParams.minPrice.toString())
    if (searchParams.maxPrice !== undefined) params.append('max_price', searchParams.maxPrice.toString())
    if (searchParams.inStock !== undefined) params.append('in_stock', searchParams.inStock.toString())
    
    const query = params.toString()
    const url = `${API_URLS.SEARCH}${query ? `?${query}` : ''}`
    
    return await $api.get(url)
  }

  // Получить товары компании
  const getCompanyGoods = async (companyId: string | number, params?: {
    skip?: number
    limit?: number
    include_hidden?: boolean
  }): Promise<ProductListResponse> => {
    const searchParams = new URLSearchParams()
    
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
    if (params?.include_hidden !== undefined) searchParams.append('include_hidden', params.include_hidden.toString())
    
    const query = searchParams.toString()
    const url = `${API_URLS.COMPANY_GOODS(companyId)}${query ? `?${query}` : ''}`
    
    return await $api.get(url)
  }

  // Получить услуги компании
  const getCompanyServices = async (companyId: string | number, params?: {
    skip?: number
    limit?: number
    include_hidden?: boolean
  }): Promise<ProductListResponse> => {
    const searchParams = new URLSearchParams()
    
    if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
    if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
    if (params?.include_hidden !== undefined) searchParams.append('include_hidden', params.include_hidden.toString())
    
    const query = searchParams.toString()
    const url = `${API_URLS.COMPANY_SERVICES(companyId)}${query ? `?${query}` : ''}`
    
    return await $api.get(url)
  }

  // Получить продукт по ID
  const getProductById = async (id: string | number): Promise<ProductResponse> => {
    return await $api.get(API_URLS.BY_ID(id))
  }

  // Получить продукт по slug
  const getProductBySlug = async (companyId: string | number, slug: string): Promise<ProductResponse> => {
    return await $api.get(API_URLS.BY_SLUG(companyId, slug))
  }

  // Получить последние продукты
  const getLatestProducts = async (limit: number = 20): Promise<ProductResponse[]> => {
    return await $api.get(`${API_URLS.LATEST}?limit=${limit}`)
  }

  return {
    getAllGoods,
    getAllServices,
    searchProducts,
    searchServices,
    getCompanyGoods,
    getCompanyServices,
    getProductById,
    getProductBySlug,
    getLatestProducts
  }
}

// SSR-ready functions
export const getLatestProductsSSR = async (limit: number = 20) => {
  const { $api } = useNuxtApp()
  return await $api.get(`${API_URLS.LATEST}?limit=${limit}`)
}

export const getAllGoodsSSR = async (skip: number = 0, limit: number = 100) => {
  const { $api } = useNuxtApp()
  return await $api.get(`${API_URLS.GOODS}?skip=${skip}&limit=${limit}`)
}

export const getAllServicesSSR = async (skip: number = 0, limit: number = 100) => {
  const { $api } = useNuxtApp()
  return await $api.get(`${API_URLS.SERVICES}?skip=${skip}&limit=${limit}`)
}

export const getCompanyGoodsSSR = async (companyId: string | number, skip: number = 0, limit: number = 100) => {
  const { $api } = useNuxtApp()
  return await $api.get(`${API_URLS.COMPANY_GOODS(companyId)}?skip=${skip}&limit=${limit}`)
}

export const getCompanyServicesSSR = async (companyId: string | number, skip: number = 0, limit: number = 100) => {
  const { $api } = useNuxtApp()
  return await $api.get(`${API_URLS.COMPANY_SERVICES(companyId)}?skip=${skip}&limit=${limit}`)
}

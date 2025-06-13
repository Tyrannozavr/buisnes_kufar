import type { CompanyResponse, CompanyUpdate } from '~/types/company'
import type { ProductResponse } from '~/types/product'  // Убедитесь, что этот тип определен
import { useNuxtApp } from 'nuxt/app'
import { useRuntimeConfig } from 'nuxt/app'
import { useCookie } from 'nuxt/app'

export const getMyCompany = async (): Promise<CompanyResponse> => {
  const { $api } = useNuxtApp()
  try {
    return await $api.get('/v1/company/me')
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('COMPANY_NOT_FOUND')
    }
    throw error
  }
}

export const updateCompany = async (data: CompanyUpdate): Promise<CompanyResponse> => {
  const { $api } = useNuxtApp()
  return await $api.put('/v1/company/me', data)
}

export const uploadCompanyLogo = async (file: File): Promise<CompanyResponse> => {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl
  const accessToken = useCookie('access_token')

  const formData = new FormData()
  formData.append('file', file)
  
  return await $fetch<CompanyResponse>(`${apiBaseUrl}/v1/company/me/logo`, {
    method: 'POST',
    body: formData,
    headers: {
      'Accept': 'application/json',
      'Authorization': accessToken.value ? `Bearer ${accessToken.value}` : ''
    }
  })
}

export const createCompany = async (data: CompanyUpdate): Promise<CompanyResponse> => {
  const { $api } = useNuxtApp()
  return await $api.post('/v1/company/me', data)
}

export const getMyProducts = async (): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  try {
    return await $api.get('/v1/company/me/products')
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('PRODUCTS_NOT_FOUND')
    }
    throw error
  }
}
import type { CompanyResponse, CompanyUpdate } from '~/types/company'
import { useNuxtApp } from 'nuxt/app'

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
  const { $api } = useNuxtApp()
  const formData = new FormData()
  formData.append('file', file)
  
  return await $api.post('/v1/company/me/logo', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const createCompany = async (data: CompanyUpdate): Promise<CompanyResponse> => {
  const { $api } = useNuxtApp()
  return await $api.post('/v1/company/me', data)
} 
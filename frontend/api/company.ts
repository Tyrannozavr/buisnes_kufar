import type { Company, CompanyUpdate } from '~/types/company'
import { useNuxtApp } from 'nuxt/app'

export const getMyCompany = async (): Promise<Company> => {
  const { $api } = useNuxtApp()
  return await $api.get('/api/v1/company/me')
}

export const updateCompany = async (data: CompanyUpdate): Promise<Company> => {
  const { $api } = useNuxtApp()
  return await $api.put('/api/v1/company/me', data)
}

export const uploadCompanyLogo = async (file: File): Promise<Company> => {
  const { $api } = useNuxtApp()
  const formData = new FormData()
  formData.append('file', file)
  
  return await $api.post('/api/v1/company/me/logo', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
} 
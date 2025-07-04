import type {CompanyResponse, CompanyStatistics} from '~/types/company'
import type {UseFetchOptions} from "nuxt/app";
import type {ProductPaginatedPublicResponse} from "~/types/product";
import type { PartnerCompany } from '~/types/company'
import { CompanyRelationType } from '~/types/company'
import { computed } from 'vue'
import { useNuxtApp } from 'nuxt/app'

export const getCompanyStatistics = async (slug: string): Promise<{ data: CompanyStatistics }> => {
    // В реальном приложении здесь был бы API-запрос
    return {
        data: {
            totalViews: 0,
            monthlyViews: 0,
            totalPurchases: 0,
            totalProducts: 0,
            registrationDate: '',
            // Добавьте другие статистические поля, если они есть в CompanyStatisticsResponse
        }
    }
}

export const getCompanyProducts = async (slug: string, options: Partial<UseFetchOptions<ProductPaginatedPublicResponse>> = {}) => {
    // В реальном приложении здесь был бы API-запрос
    return useApi<ProductPaginatedPublicResponse>(`/v1/products/company/${slug}`, {
        method: 'GET',
        ...options
    })
}

export const getCompanyProductsPaginated = async (slug: string, page: number = 1, perPage: number = 12) => {
    const skip = (page - 1) * perPage
    return useApi<ProductPaginatedPublicResponse>(`/v1/products/company/${slug}`, {
        method: 'GET',
        params: {
            skip,
            limit: perPage
        }
    })
}

export const getCompany = async (slug: string, options: Partial<UseFetchOptions<CompanyResponse>> = {}) => {
    return useApi<CompanyResponse>(`/v1/companies/slug/${slug}`, {
        method: 'GET',
        ...options
    })
}

export const addCompanyRelation = async (relatedCompanyId: number, relationType: CompanyRelationType) => {
  return useApi(`/v1/company/me/relations`, {
    method: 'POST',
    body: {
      related_company_id: relatedCompanyId,
      relation_type: relationType
    }
  })
}

export const removeCompanyRelation = async (relatedCompanyId: number, relationType: CompanyRelationType) => {
    console.log(relatedCompanyId, relationType, "called remove relation")
  return useApi(`/v1/company/me/relations`, {
    method: 'DELETE',
    params: {
      related_company_id: relatedCompanyId,
      relation_type: relationType
    }
  })
}

export const getCompanyRelations = async (relationType?: CompanyRelationType) => {
  const { $api } = useNuxtApp()
  const params = relationType ? { relation_type: relationType } : {}
  // Возвращаем сразу массив, а не Ref
  const response = await $api.get('/v1/company/me/relations', { params })
  return { data: response }
}

export const getPartners = async (page = 1, perPage = 10) => {
  const { data, error, pending, refresh } = useApi<any>(`/v1/company/me/partners`, {
    method: 'GET',
    params: { page, per_page: perPage }
  })
  return {
    data: computed(() => (data.value?.data ?? []).map(mapCompanyToPartnerCompany)),
    pagination: computed(() => data.value?.pagination),
    error,
    pending,
    refresh
  }
}

export const getSuppliers = async (page = 1, perPage = 10) => {
  const { data, error, pending, refresh } = useApi<any>(`/v1/company/me/suppliers`, {
    method: 'GET',
    params: { page, per_page: perPage }
  })
  return {
    data: computed(() => (data.value?.data ?? []).map(mapCompanyToPartnerCompany)),
    pagination: computed(() => data.value?.pagination),
    error,
    pending,
    refresh
  }
}

export const getBuyers = async (page = 1, perPage = 10) => {
  const { data, error, pending, refresh } = useApi<any>(`/v1/company/me/buyers`, {
    method: 'GET',
    params: { page, per_page: perPage }
  })
  return {
    data: computed(() => (data.value?.data ?? []).map(mapCompanyToPartnerCompany)),
    pagination: computed(() => data.value?.pagination),
    error,
    pending,
    refresh
  }
}

function mapCompanyToPartnerCompany(company: any): PartnerCompany {
  return {
    id: company.id,
    fullName: company.full_name || company.name || '',
    slug: company.slug || '',
    logo: company.logo_url || company.logo || null,
    businessType: company.business_type || '',
    country: company.country || '',
    region: company.region || '',
    city: company.city || ''
  }
}


import type {CompanyResponse, CompanyStatistics} from '~/types/company'
import type {UseFetchOptions} from "nuxt/app";
import type {ProductPaginatedPublicResponse} from "~/types/product";

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


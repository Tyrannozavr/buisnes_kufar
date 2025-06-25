import type { Announcement, AnnouncementFormData, AnnouncementListResponse, AnnouncementCategory } from '~/types/announcement'
import type { PaginationResponse } from '~/types/api'

export const PUBLIC_ANNOUNCEMENTS_API = {
    ANNOUNCEMENTS: '/v1/announcements',
    ANNOUNCEMENT: '/v1/announcements/{announcement_id}',
    COMPANY_ANNOUNCEMENTS: '/v1/announcements/company/{company_id}',
    CATEGORY_ANNOUNCEMENTS: '/v1/announcements/category/{category}',
    CATEGORIES: '/v1/announcements/categories/list',
} as const

export const usePublicAnnouncementsApi = () => {
    const { $api } = useNuxtApp()

    // Get all published announcements
    const getAllAnnouncements = async (page: number = 1, perPage: number = 10): Promise<AnnouncementListResponse> => {
        return await $api.get(PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS, { 
            params: { page, per_page: perPage } 
        })
    }

    // Get a single published announcement by ID
    const getAnnouncementById = async (announcementId: number): Promise<Announcement> => {
        const url = PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', announcementId.toString())
        return await $api.get(url)
    }

    // Get published announcements for a specific company
    const getCompanyAnnouncements = async (companyId: number, page: number = 1, perPage: number = 10): Promise<AnnouncementListResponse> => {
        const url = PUBLIC_ANNOUNCEMENTS_API.COMPANY_ANNOUNCEMENTS.replace('{company_id}', companyId.toString())
        return await $api.get(url, { 
            params: { page, per_page: perPage } 
        })
    }

    // Get published announcements by category
    const getAnnouncementsByCategory = async (category: string, page: number = 1, perPage: number = 10): Promise<AnnouncementListResponse> => {
        const url = PUBLIC_ANNOUNCEMENTS_API.CATEGORY_ANNOUNCEMENTS.replace('{category}', category)
        return await $api.get(url, { 
            params: { page, per_page: perPage } 
        })
    }

    // Get announcement categories
    const getAnnouncementCategories = async (): Promise<AnnouncementCategory[]> => {
        return await $api.get(PUBLIC_ANNOUNCEMENTS_API.CATEGORIES)
    }

    return {
        getAllAnnouncements,
        getAnnouncementById,
        getCompanyAnnouncements,
        getAnnouncementsByCategory,
        getAnnouncementCategories
    }
}

// SSR-ready functions
export const getLatestAnnouncementsSSR = async (limit: number = 6) => {
    const { $api } = useNuxtApp()
    return await $api.get(PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS, {
        params: { page: 1, per_page: limit }
    })
}

export const getCompanyAnnouncementsSSR = async (companyId: number, page: number = 1, perPage: number = 10) => {
    const { $api } = useNuxtApp()
    const url = PUBLIC_ANNOUNCEMENTS_API.COMPANY_ANNOUNCEMENTS.replace('{company_id}', companyId.toString())
    return await $api.get(url, {
        params: { page, per_page: perPage }
    }) as AnnouncementListResponse
}

export const getAnnouncementByIdSSR = async (announcementId: number) => {
    const { $api } = useNuxtApp()
    const url = PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', announcementId.toString())
    return await $api.get(url)
}

export const getAnnouncementCategoriesSSR = async () => {
    const { $api } = useNuxtApp()
    return await $api.get(PUBLIC_ANNOUNCEMENTS_API.CATEGORIES)
}

// Legacy functions for backward compatibility
export const useAnnouncementsApi = () => {
    const { $api } = useNuxtApp()

    const getAllAnnouncements = async (options: any = {}) => {
        return await $api.get(PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS, options)
    }

    const getAnnouncements = async (options: any = {}) => {
        return await $api.get(PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS, options)
    }

    const getLatestAnnouncements = async (limit: number = 5, options: any = {}) => {
        return await $api.get(PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS, {
            params: { page: 1, per_page: limit },
            ...options
        })
    }

    const getAnnouncementById = async (id: string, options: any = {}) => {
        const url = PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', id)
        return await $api.get(url, options)
    }

    const getCompanyAnnouncements = async (page: number = 1, perPage: number = 10, options: any = {}) => {
        return await $api.get(`${PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS}/company`, {
            params: { page, perPage },
            ...options
        }) as PaginationResponse<Announcement>
    }

    const createAnnouncement = async (data: Partial<Announcement>, options: any = {}) => {
        return await $api.post(PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS, data, options)
    }

    const updateAnnouncement = async (id: string, data: Partial<Announcement>, options: any = {}) => {
        const url = PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', id)
        return await $api.put(url, data, options)
    }

    const deleteAnnouncement = async (id: string, options: any = {}) => {
        const url = PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', id)
        await $api.delete(url, options)
    }

    const publishAnnouncement = async (id: string, options: any = {}) => {
        const url = PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', id)
        return await $api.put(url, {}, options)
    }

    return {
        getAllAnnouncements,
        getAnnouncements,
        getLatestAnnouncements,
        getAnnouncementById,
        getCompanyAnnouncements,
        createAnnouncement,
        updateAnnouncement,
        deleteAnnouncement,
        publishAnnouncement
    }
}

export const useAnnouncements = (page: number, perPage: number) => {
    return useApi<AnnouncementListResponse>(`${PUBLIC_ANNOUNCEMENTS_API.ANNOUNCEMENTS}?page=${page}&per_page=${perPage}`)
} 
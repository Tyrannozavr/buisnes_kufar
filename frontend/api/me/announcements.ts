import type { Announcement, AnnouncementFormData, AnnouncementListResponse, AnnouncementCategory } from '~/types/announcement'

export const ANNOUNCEMENTS_API = {
    ANNOUNCEMENTS: '/v1/company/announcements',
    ANNOUNCEMENT: '/v1/company/announcements/{announcement_id}',
    ANNOUNCEMENT_IMAGE: '/v1/company/announcements/{announcement_id}/images',
    CATEGORIES: '/v1/company/announcements/categories',
} as const

export const useAnnouncementsApi = () => {
    const { $api } = useNuxtApp()

    // Get all announcements for company
    const getAnnouncements = async (page: number = 1, perPage: number = 10): Promise<AnnouncementListResponse> => {
        return await $api.get(ANNOUNCEMENTS_API.ANNOUNCEMENTS, { params: { page, per_page: perPage } })
    }

    // Create a new announcement
    const createAnnouncement = async (announcementData: AnnouncementFormData): Promise<Announcement> => {
        return await $api.post(ANNOUNCEMENTS_API.ANNOUNCEMENTS, announcementData)
    }

    // Update an existing announcement
    const updateAnnouncement = async (announcementId: number, announcementData: Partial<AnnouncementFormData>): Promise<Announcement> => {
        const url = ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', announcementId.toString())
        return await $api.put(url, announcementData)
    }

    // Delete an announcement
    const deleteAnnouncement = async (announcementId: number): Promise<void> => {
        const url = ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', announcementId.toString())
        await $api.delete(url)
    }

    // Get a single announcement by ID
    const getAnnouncementById = async (announcementId: number): Promise<Announcement> => {
        const url = ANNOUNCEMENTS_API.ANNOUNCEMENT.replace('{announcement_id}', announcementId.toString())
        return await $api.get(url)
    }

    // Upload image for announcement
    const uploadAnnouncementImage = async (announcementId: number, file: File): Promise<Announcement> => {
        const url = ANNOUNCEMENTS_API.ANNOUNCEMENT_IMAGE.replace('{announcement_id}', announcementId.toString())
        const formData = new FormData()
        formData.append('file', file)
        return await $api.post(url, formData)
    }

    // Upload multiple images for announcement
    const uploadAnnouncementImages = async (announcementId: number, files: File[]): Promise<Announcement> => {
        // Upload files one by one since backend expects single file
        let lastResult: Announcement | null = null;
        
        for (const file of files) {
            const url = ANNOUNCEMENTS_API.ANNOUNCEMENT_IMAGE.replace('{announcement_id}', announcementId.toString())
            const formData = new FormData()
            formData.append('file', file)
            
            lastResult = await $api.post(url, formData)
        }
        
        return lastResult!
    }

    // Get announcement categories
    const getAnnouncementCategories = async (): Promise<AnnouncementCategory[]> => {
        return await $api.get(ANNOUNCEMENTS_API.CATEGORIES)
    }

    return {
        getAnnouncements,
        createAnnouncement,
        updateAnnouncement,
        deleteAnnouncement,
        getAnnouncementById,
        uploadAnnouncementImage,
        uploadAnnouncementImages,
        getAnnouncementCategories
    }
} 
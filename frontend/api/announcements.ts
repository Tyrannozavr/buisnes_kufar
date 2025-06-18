import type { Announcement } from '~/types/announcement'
import type { PaginationResponse } from '~/types/api'
import { API_URLS } from '~/constants/urls'

export const useAnnouncementsApi = () => {
  const { $api } = useNuxtApp()

  const getAllAnnouncements = async (options: any = {}) => {
    return await $api.get(API_URLS.ANNOUNCEMENTS, options)
  }

  const getAnnouncements = async (options: any = {}) => {
    return await $api.get(API_URLS.ANNOUNCEMENTS, options)
  }

  const getLatestAnnouncements = async (limit: number = 5, options: any = {}) => {
    return await $api.get(API_URLS.ANNOUNCEMENTS_LATEST, {
      params: { limit },
      ...options
    })
  }

  const getAnnouncementById = async (id: string, options: any = {}) => {
    return await $api.get(`${API_URLS.ANNOUNCEMENTS}/${id}`, options)
  }

  const getCompanyAnnouncements = async (page: number = 1, perPage: number = 10, options: any = {}) => {
    return await $api.get(`${API_URLS.ANNOUNCEMENTS}/company`, {
      params: { page, perPage },
      ...options
    }) as PaginationResponse<Announcement>
  }

  const createAnnouncement = async (data: Partial<Announcement>, options: any = {}) => {
    return await $api.post(API_URLS.ANNOUNCEMENTS, data, options)
  }

  const updateAnnouncement = async (id: string, data: Partial<Announcement>, options: any = {}) => {
    return await $api.put(`${API_URLS.ANNOUNCEMENTS}/${id}`, data, options)
  }

  const deleteAnnouncement = async (id: string, options: any = {}) => {
    return await $api.delete(`${API_URLS.ANNOUNCEMENTS}/${id}`, options)
  }

  const publishAnnouncement = async (id: string, options: any = {}) => {
    return await $api.put(`${API_URLS.ANNOUNCEMENTS}/${id}/publish`, {}, options)
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

// SSR-ready functions
export const getLatestAnnouncementsSSR = async (limit: number = 6) => {
  const { $api } = useNuxtApp()
  return await $api.get(API_URLS.ANNOUNCEMENTS_LATEST, {
    params: { limit }
  })
}

export const getCompanyAnnouncementsSSR = async (page: number = 1, perPage: number = 10) => {
  const { $api } = useNuxtApp()
  return await $api.get(`${API_URLS.ANNOUNCEMENTS}/company`, {
    params: { page, perPage }
  }) as PaginationResponse<Announcement>
}

export const useAnnouncements = (page: number, perPage: number) => {
  return useApi<PaginationResponse<Announcement>>(`/announcements?page=${page}&perPage=${perPage}`)
} 
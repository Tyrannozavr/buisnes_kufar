import type { Announcement } from '~/types/announcement'
import type { UseFetchOptions } from 'nuxt/app'

export const useAnnouncementsApi = () => {
  const getAllAnnouncements = (options: UseFetchOptions<Announcement[]> = {}) => {
    return useApi<Announcement[]>('/announcements', {
      ...options
    })
  }

  const getAnnouncements = (options: UseFetchOptions<Announcement[]> = {}) => {
    return useApi<Announcement[]>('/announcements', {
      transform: (data) =>
        data
          .filter(a => a.published)
          .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()),
      ...options
    })
  }

  const getLatestAnnouncements = (limit: number = 5, options: UseFetchOptions<Announcement[]> = {}) => {
    return useApi<Announcement[]>('/announcements', {
      transform: (data) =>
        data
          .filter(a => a.published)
          .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
          .slice(0, limit),
      ...options
    })
  }

  const getAnnouncementById = (id: string, options: UseFetchOptions<Announcement> = {}) => {
    return useApi<Announcement>(`/announcements/${id}`, options)
  }

  const getCompanyAnnouncements = (page: number = 1, perPage: number = 10, options: UseFetchOptions<{
    data: Announcement[],
    pagination: {
      total: number,
      page: number,
      perPage: number,
      totalPages: number
    }
  }> = {}) => {
    return useApi<{
      data: Announcement[],
      pagination: {
        total: number,
        page: number,
        perPage: number,
        totalPages: number
      }
    }>(`/announcements/company?page=${page}&perPage=${perPage}`, {
      lazy: true,
      ...options
    })
  }

  const createAnnouncement = (data: Partial<Announcement>, options: UseFetchOptions<Announcement> = {}) => {
    return useApi<Announcement>('/announcements', {
      method: 'POST',
      body: data,
      ...options
    })
  }

  const updateAnnouncement = (id: string, data: Partial<Announcement>, options: UseFetchOptions<Announcement> = {}) => {
    return useApi<Announcement>(`/announcements/${id}`, {
      method: 'PUT',
      body: data,
      ...options
    })
  }

  const publishAnnouncement = (id: string, options: UseFetchOptions<void> = {}) => {
    return useApi<void>(`/announcements/${id}/publish`, {
      method: 'PUT',
      ...options
    })
  }

  const unpublishAnnouncement = (id: string, options: UseFetchOptions<void> = {}) => {
    return useApi<void>(`/announcements/${id}/unpublish`, {
      method: 'PUT',
      ...options
    })
  }

  const deleteAnnouncement = (id: string, options: UseFetchOptions<void> = {}) => {
    return useApi<void>(`/announcements/${id}`, {
      method: 'DELETE',
      ...options
    })
  }

  return {
    getAllAnnouncements,
    getAnnouncements,
    getLatestAnnouncements,
    getAnnouncementById,
    getCompanyAnnouncements,
    createAnnouncement,
    updateAnnouncement,
    publishAnnouncement,
    unpublishAnnouncement,
    deleteAnnouncement
  }
} 
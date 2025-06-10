import type { Announcement } from '~/types/announcement'
import type { Company } from '~/types/company'
import { useApi } from '~/composables/useApi'

export const useHomeApi = () => {
  const getLatestAnnouncements = () => {
    return useApi<{
      data: Announcement[],
      pagination: {
        total: number,
        page: number,
        perPage: number,
        totalPages: number
      },
    }>('/announcements/latest', {
      params: {
        limit: 6
      }
    })
  }

  const getLatestCompanies = () => {
    return useApi<Company[]>('/companies/latest', {
      params: {
        limit: 6
      }
    })
  }

  return {
    getLatestAnnouncements,
    getLatestCompanies
  }
} 
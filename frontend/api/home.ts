import type { Announcement } from '~/types/announcement'
import type { Company } from '~/types/company'

export const useHomeApi = () => {
  const getLatestAnnouncements = () => {
    return useApi<{
      data: Announcement[],
      pagination: {
        total: number,
        page: number,
        perPage: number,
        totalPages: number
      }
    }>('/announcements/latest')
  }

  const getLatestCompanies = () => {
    return useApi<Company[]>('/companies/latest')
  }

  return {
    getLatestAnnouncements,
    getLatestCompanies
  }
} 
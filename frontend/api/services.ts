import type { ServiceSearchParams, ServiceResponse } from '~/types/filters'

export const useServicesApi = () => {
  const searchServices = async (params: ServiceSearchParams) => {
    // TODO: Implement actual API call
    return {
      data: ref<ServiceResponse>({
        data: [],
        pagination: {
          currentPage: 1,
          totalPages: 1,
          totalItems: 0,
          itemsPerPage: 10
        }
      })
    }
  }

  return {
    searchServices
  }
} 
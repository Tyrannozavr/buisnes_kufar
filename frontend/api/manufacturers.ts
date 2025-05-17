import type {Manufacturer, ManufacturersSearchParams} from '~/types/company'

export const useManufacturersApi = () => {
  const searchManufacturers = async (params: ManufacturersSearchParams = {}) => {
    return useApi<Manufacturer[]>('/manufacturers', {
      query: params
    });
  }

  return {
    searchManufacturers
  }
} 
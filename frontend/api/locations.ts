import type { Country, Region, City, FederalDistrict } from '~/types/location'

export const useLocationsApi = () => {
  const getCountries = async () => {
    return await useApi<Country[]>('/locations/countries')
  }

  const getFederalDistricts = async () => {
    return await useApi<FederalDistrict[]>('/locations/federal-districts')
  }

  const getRegions = async (country: string, federalDistrict: string = "") => {
    return await useApi<Region[]>(`/locations/regions`, {
      query: { country, federalDistrict }
    })
  }

  const getCities = async (country: string) => {
    if (!country) return { data: ref<City[]>([]) }
    return await useApi<City[]>(`/locations/cities`, {
      query: { country }
    })
  }

  return {
    getCountries,
    getFederalDistricts,
    getRegions,
    getCities
  }
} 
import type { Country, Region, City, FederalDistrict } from '~/types/location'

interface LocationItem {
  label: string
  value: string
}

export const useLocationsApi = () => {
  const getCountries = async () => {
    const { data } = await useApi<LocationItem[]>('/locations/countries')
    return { data }
  }

  const getFederalDistricts = async () => {
    const { data } = await useApi<LocationItem[]>('/locations/federal-districts')
    return { data }
  }

  const getRegions = async (country: string, federalDistrict: string = "") => {
    const { data } = await useApi<LocationItem[]>(`/locations/regions`, {
      query: { country, federalDistrict }
    })
    return { data }
  }

  const getCities = async (country: string) => {
    if (!country) return { data: ref<LocationItem[]>([]) }
    const { data } = await useApi<LocationItem[]>(`/locations/cities`, {
      query: { country }
    })
    return { data }
  }

  return {
    getCountries,
    getFederalDistricts,
    getRegions,
    getCities
  }
} 
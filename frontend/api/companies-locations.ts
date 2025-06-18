import type { LocationItem, LocationResponse } from '~/types/location'

export const useCompaniesLocations = () => {
  const { $api } = useNuxtApp()
  const countriesLoading = ref(false)
  const federalDistrictsLoading = ref(false)
  const regionsLoading = ref(false)
  const citiesLoading = ref(false)
  const countriesError = ref<Error | null>(null)
  const federalDistrictsError = ref<Error | null>(null)
  const regionsError = ref<Error | null>(null)
  const citiesError = ref<Error | null>(null)

  const countryOptions = ref<LocationItem[]>([])
  const federalDistrictOptions = ref<LocationItem[]>([])
  const regionOptions = ref<LocationItem[]>([])
  const cityOptions = ref<LocationItem[]>([])

  // Загрузка списка стран
  const loadCountries = async () => {
    countriesLoading.value = true
    countriesError.value = null
    try {
      const response = await $api.get('/v1/companies/locations/countries')
      const data = response as LocationResponse
      countryOptions.value = data.items || []
    } catch (error) {
      countriesError.value = error as Error
      console.error('Error loading countries:', error)
    } finally {
      countriesLoading.value = false
    }
  }

  // Загрузка федеральных округов для России
  const loadFederalDistricts = async () => {
    federalDistrictsLoading.value = true
    federalDistrictsError.value = null
    try {
      const response = await $api.get('/v1/companies/locations/federal-districts')
      const data = response as LocationResponse
      federalDistrictOptions.value = data.items || []
    } catch (error) {
      federalDistrictsError.value = error as Error
      console.error('Error loading federal districts:', error)
    } finally {
      federalDistrictsLoading.value = false
    }
  }

  // Загрузка регионов для выбранной страны
  const loadRegions = async (countryCode: string, federalDistrict?: string) => {
    regionsLoading.value = true
    regionsError.value = null
    try {
      const response = await $api.get(`/v1/companies/locations/regions/${countryCode}`, {
        params: { federal_district: federalDistrict }
      })
      const data = response as LocationResponse
      regionOptions.value = data.items || []
    } catch (error) {
      regionsError.value = error as Error
      console.error('Error loading regions:', error)
    } finally {
      regionsLoading.value = false
    }
  }

  // Загрузка городов для выбранного региона (простой список без поиска)
  const loadCities = async (countryCode: string, regionId: string) => {
    citiesLoading.value = true
    citiesError.value = null
    try {
      const response = await $api.get(`/v1/companies/locations/cities`, {
        params: { 
          region: regionId, 
          country: countryCode
        }
      })
      const data = response as LocationResponse
      cityOptions.value = data.items || []
    } catch (error) {
      citiesError.value = error as Error
      console.error('Error loading cities:', error)
    } finally {
      citiesLoading.value = false
    }
  }

  // Загрузка начальных данных
  onMounted(() => {
    loadCountries()
  })

  return {
    // Состояния загрузки
    countriesLoading,
    federalDistrictsLoading,
    regionsLoading,
    citiesLoading,
    
    // Ошибки
    countriesError,
    federalDistrictsError,
    regionsError,
    citiesError,
    
    // Данные
    countryOptions,
    federalDistrictOptions,
    regionOptions,
    cityOptions,
    
    // Методы
    loadCountries,
    loadFederalDistricts,
    loadRegions,
    loadCities
  }
} 
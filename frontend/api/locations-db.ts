import type { LocationItem, LocationResponse } from '~/types/location'

export const useLocationsDbApi = () => {
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

  // Загрузка списка стран из локальной БД
  const loadCountries = async () => {
    countriesLoading.value = true
    countriesError.value = null
    try {
      const response = await $api.get('/v1/locations/countries')
      const data = response as LocationResponse
      countryOptions.value = data.items || []
    } catch (error) {
      countriesError.value = error as Error
      console.error('Error loading countries from DB:', error)
    } finally {
      countriesLoading.value = false
    }
  }

  // Загрузка федеральных округов для России из локальной БД
  const loadFederalDistricts = async (countryCode: string) => {
    federalDistrictsLoading.value = true
    federalDistrictsError.value = null
    try {
      const response = await $api.get('/v1/locations/federal-districts', {
        params: { country_code: countryCode }
      })
      const data = response as LocationResponse
      federalDistrictOptions.value = data.items || []
    } catch (error) {
      federalDistrictsError.value = error as Error
      console.error('Error loading federal districts from DB:', error)
    } finally {
      federalDistrictsLoading.value = false
    }
  }

  // Загрузка регионов для выбранной страны из локальной БД
  const loadRegions = async (countryCode: string, federalDistrictCode?: string) => {
    regionsLoading.value = true
    regionsError.value = null
    try {
      const params: any = { country_code: countryCode }
      if (federalDistrictCode) {
        params.federal_district_code = federalDistrictCode
      }
      
      const response = await $api.get('/v1/locations/regions', { params })
      const data = response as LocationResponse
      regionOptions.value = data.items || []
    } catch (error) {
      regionsError.value = error as Error
      console.error('Error loading regions from DB:', error)
    } finally {
      regionsLoading.value = false
    }
  }

  // Загрузка городов для выбранного региона из локальной БД
  const loadCities = async (
    countryCode: string, 
    regionCode?: string, 
    federalDistrictCode?: string,
    search?: string,
    millionCitiesOnly?: boolean,
    regionalCentersOnly?: boolean
  ) => {
    citiesLoading.value = true
    citiesError.value = null
    try {
      const params: any = { country_code: countryCode }
      if (regionCode) {
        params.region_code = regionCode
      }
      if (federalDistrictCode) {
        params.federal_district_code = federalDistrictCode
      }
      if (search) {
        params.search = search
      }
      if (millionCitiesOnly) {
        params.million_cities_only = millionCitiesOnly
      }
      if (regionalCentersOnly) {
        params.regional_centers_only = regionalCentersOnly
      }
      
      const response = await $api.get('/v1/locations/cities', { params })
      const data = response as LocationResponse
      cityOptions.value = data.items || []
    } catch (error) {
      citiesError.value = error as Error
      console.error('Error loading cities from DB:', error)
    } finally {
      citiesLoading.value = false
    }
  }

  // Поиск городов по названию в локальной БД
  const searchCities = async (cityName: string, countryCode: string) => {
    citiesLoading.value = true
    citiesError.value = null
    try {
      const response = await $api.get('/v1/locations/cities', {
        params: { 
          country_code: countryCode,
          search: cityName
        }
      })
      const data = response as LocationResponse
      cityOptions.value = data.items || []
    } catch (error) {
      citiesError.value = error as Error
      console.error('Error searching cities in DB:', error)
    } finally {
      citiesLoading.value = false
    }
  }

  // Создание нового региона
  const createRegion = async (countryCode: string, regionName: string, federalDistrictCode?: string) => {
    try {
      const payload = {
        country_code: countryCode,
        federal_district_code: federalDistrictCode,
        name: regionName,
        code: regionName.toUpperCase().replace(/[^A-ZА-Я0-9]/g, '') // Генерируем код из названия
      }
      
      console.log('📤 Отправка запроса на создание региона:', payload)
      
      const response = await $api.post('/v1/locations/regions', payload)
      
      console.log('📥 Ответ от сервера:', response.data)
      
      return response.data
    } catch (error) {
      console.error('❌ Error creating region:', error)
      throw error
    }
  }

  // Создание нового города
  const createCity = async (
    countryCode: string,
    regionName: string,
    cityName: string,
    federalDistrictCode?: string,
    population?: number,
    isMillionCity?: boolean,
    isRegionalCenter?: boolean
  ) => {
    try {
      const response = await $api.post('/v1/locations/cities', {
        country_code: countryCode,
        region_name: regionName,
        federal_district_code: federalDistrictCode,
        name: cityName,
        population: population,
        is_million_city: isMillionCity || false,
        is_regional_center: isRegionalCenter || false
      })
      return response.data
    } catch (error) {
      console.error('Error creating city:', error)
      throw error
    }
  }

  // Загрузка полного дерева локаций
  const loadLocationTree = async () => {
    try {
      const response = await $api.get('/v1/locations/location-tree')
      return response
    } catch (error) {
      console.error('Error loading location tree from DB:', error)
      throw error
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
    loadCities,
    searchCities,
    createRegion,
    createCity,
    loadLocationTree
  }
}

import type { LocationResponse } from '~/types/location'

export const useLocationsApi = () => {
  // Загружаем страны на сервере
  const { data: countries, error: countriesError, pending: countriesLoading } = useApi<LocationResponse>('/locations/countries', {
    server: true, // Загружаем на сервере
    immediate: true // Загружаем сразу
  })

  // Федеральные округи загружаем только для России
  const { data: federalDistricts, error: federalDistrictsError, pending: federalDistrictsLoading, refresh: refreshFederalDistricts } = useApi<LocationResponse>('/locations/federal-districts', {
    server: false,
    immediate: false // Не загружаем сразу
  })

  // Регионы загружаем только при выборе страны
  const { data: regions, error: regionsError, pending: regionsLoading, refresh: refreshRegions } = useApi<LocationResponse>('/locations/regions', {
    server: false,
    immediate: false, // Не загружаем сразу
    watch: false // Отключаем автоматическое обновление
  })

  // Города загружаем только при выборе региона
  const { data: cities, error: citiesError, pending: citiesLoading, refresh: refreshCities } = useApi<LocationResponse>('/locations/cities', {
    server: false,
    immediate: false, // Не загружаем сразу
    watch: false // Отключаем автоматическое обновление
  })

  // Функция для загрузки регионов
  const loadRegions = async (country: string) => {
    if (!country) return
    const query = { country }
    await refreshRegions()
  }

  // Функция для загрузки городов
  const loadCities = async (country: string, region: string) => {
    if (!country || !region) return
    const query = { country, region }
    await refreshCities()
  }

  return {
    // Данные
    countries,
    federalDistricts,
    regions,
    cities,
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
    // Методы
    refreshFederalDistricts,
    loadRegions,
    loadCities
  }
} 
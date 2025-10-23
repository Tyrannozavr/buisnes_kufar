<script setup lang="ts">
import type { ProductSearchParams, ServiceSearchParams, LocationItem } from '~/types/filters'
import { isLocationItem } from '~/types/filters'
import { useProductFilters, useServiceFilters } from '~/api/filters'
import CitiesFilterTree from './CitiesFilterTree.vue'

const props = defineProps<{
  type: 'products' | 'services'
  title: string
  locationPrefix?: string
}>()

const emit = defineEmits<{
  (e: 'search', params: ProductSearchParams | ServiceSearchParams): void
}>()

// API для фильтров
const { 
  getProductFilters, 
  getCitiesByLocation, 
  getRegionsByCountry, 
  getFederalDistrictsByCountry 
} = useProductFilters()
const { getServiceFilters } = useServiceFilters()

// API instance
const { $api } = useNuxtApp()

// Состояние загрузки фильтров
const filtersLoading = ref(false)
const filtersError = ref<string | null>(null)

// Данные фильтров
const filterData = ref<{
  countries: LocationItem[]
  federal_districts: LocationItem[]
  regions: LocationItem[]
  cities: LocationItem[]
}>({
  countries: [],
  federal_districts: [],
  regions: [],
  cities: []
})

// Кэш для динамических данных (30 минут)
const cache = ref<Map<string, { data: any, timestamp: number }>>(new Map())
const CACHE_DURATION = 30 * 60 * 1000 // 30 минут в миллисекундах

// Функция для проверки валидности кэша
const isCacheValid = (key: string): boolean => {
  const cached = cache.value.get(key)
  if (!cached) return false
  return Date.now() - cached.timestamp < CACHE_DURATION
}

// Функция для получения данных из кэша или API
const getCachedData = async <T>(key: string, fetchFn: () => Promise<T>): Promise<T> => {
  if (isCacheValid(key)) {
    return cache.value.get(key)!.data
  }
  
  const data = await fetchFn()
  cache.value.set(key, { data, timestamp: Date.now() })
  return data
}

// Search state
const searchQuery = ref('')
const selectedCities = ref<number[]>([])
const minPrice = ref<number | null>(null)
const maxPrice = ref<number | null>(null)
const inStock = ref(false)

// Location tree data
const allRegions = ref<LocationItem[]>([])
const allCities = ref<LocationItem[]>([])

// Cities filter data
const citiesData = ref<any>(null)
const citiesLoading = ref(false)
const citiesError = ref<string | null>(null)

// Filter mode
const isAdvancedMode = ref(false)

// Cities filter state
const expandedCountries = ref<number[]>([])
const expandedFederalDistricts = ref<number[]>([])
const expandedRegions = ref<number[]>([])

// Computed properties

// Methods
const loadFilters = async () => {
  filtersLoading.value = true
  filtersError.value = null
  
  try {
    let response
    if (props.type === 'products') {
      response = await getProductFilters()
    } else {
      response = await getServiceFilters()
    }
    
    filterData.value = {
      countries: response.countries,
      federal_districts: response.federal_districts,
      regions: response.regions,
      cities: response.cities
    }
  } catch (error) {
    filtersError.value = `Ошибка загрузки фильтров: ${error}`
    console.error('Error loading filters:', error)
  } finally {
    filtersLoading.value = false
  }
}

// Handle location tree selection
const handleLocationSelection = (selection: { countries: string[]; regions: string[]; cities: string[] }) => {
  console.log('Location selection changed:', selection)
  // Здесь можно добавить дополнительную логику обработки выбора
}

const handleSearch = () => {
  const params = {
    search: searchQuery.value,
    cities: selectedCities.value,
    minPrice: minPrice.value || undefined,
    maxPrice: maxPrice.value || undefined,
    inStock: inStock.value || undefined
  }

  emit('search', params)
}

// Cities filter functions
const loadCitiesData = async () => {
  console.log('Loading cities data...')
  citiesLoading.value = true
  citiesError.value = null
  
  try {
    const response = await $api.get('/v1/cities-filter/cities-filter')
    console.log('Cities data loaded:', response)
    citiesData.value = response
  } catch (e) {
    citiesError.value = 'Ошибка загрузки данных о городах'
    console.error('Error fetching cities data:', e)
  } finally {
    citiesLoading.value = false
  }
}

// Toggle functions
const toggleCountry = (countryId: number) => {
  console.log('Toggling country:', countryId)
  const index = expandedCountries.value.indexOf(countryId)
  if (index > -1) {
    expandedCountries.value.splice(index, 1)
    console.log('Country collapsed')
  } else {
    expandedCountries.value.push(countryId)
    console.log('Country expanded')
  }
}

const toggleFederalDistrict = (fdId: number) => {
  const index = expandedFederalDistricts.value.indexOf(fdId)
  if (index > -1) {
    expandedFederalDistricts.value.splice(index, 1)
  } else {
    expandedFederalDistricts.value.push(fdId)
  }
}

const toggleRegion = (regionId: number) => {
  const index = expandedRegions.value.indexOf(regionId)
  if (index > -1) {
    expandedRegions.value.splice(index, 1)
  } else {
    expandedRegions.value.push(regionId)
  }
}

// Selection functions
const toggleCitySelection = (cityId: number) => {
  if (selectedCities.value.includes(cityId)) {
    selectedCities.value = selectedCities.value.filter(id => id !== cityId)
  } else {
    selectedCities.value = [...selectedCities.value, cityId]
  }
}

const toggleRegionSelection = (regionId: number) => {
  const region = findRegionById(regionId)
  if (!region) return
  
  const regionCityIds = region.cities.map((city: any) => city.id)
  const allSelected = regionCityIds.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    selectedCities.value = selectedCities.value.filter(id => !regionCityIds.includes(id))
  } else {
    const newSelections = regionCityIds.filter(id => !selectedCities.value.includes(id))
    selectedCities.value = [...selectedCities.value, ...newSelections]
  }
}

const toggleFederalDistrictSelection = (fdId: number) => {
  const fd = findFederalDistrictById(fdId)
  if (!fd) return
  
  const fdCityIds = fd.regions.flatMap((region: any) => region.cities.map((city: any) => city.id))
  const allSelected = fdCityIds.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    selectedCities.value = selectedCities.value.filter(id => !fdCityIds.includes(id))
  } else {
    const newSelections = fdCityIds.filter(id => !selectedCities.value.includes(id))
    selectedCities.value = [...selectedCities.value, ...newSelections]
  }
}

const toggleCountrySelection = (countryId: number) => {
  const country = findCountryById(countryId)
  if (!country) return
  
  const countryCityIds = country.federal_districts.flatMap((fd: any) => 
    fd.regions.flatMap((region: any) => region.cities.map((city: any) => city.id))
  )
  const allSelected = countryCityIds.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    selectedCities.value = selectedCities.value.filter(id => !countryCityIds.includes(id))
  } else {
    const newSelections = countryCityIds.filter(id => !selectedCities.value.includes(id))
    selectedCities.value = [...selectedCities.value, ...newSelections]
  }
}

const clearAllSelections = () => {
  selectedCities.value = []
}

// Helper functions
const findCountryById = (id: number): any => {
  return citiesData.value?.countries.find((c: any) => c.id === id) || null
}

const findFederalDistrictById = (id: number): any => {
  for (const country of citiesData.value?.countries || []) {
    const fd = country.federal_districts.find((fd: any) => fd.id === id)
    if (fd) return fd
  }
  return null
}

const findRegionById = (id: number): any => {
  for (const country of citiesData.value?.countries || []) {
    for (const fd of country.federal_districts) {
      const region = fd.regions.find((r: any) => r.id === id)
      if (region) return region
    }
  }
  return null
}

// Check selection state
const isCountrySelected = (countryId: number): boolean => {
  const country = findCountryById(countryId)
  if (!country) return false
  
  const countryCityIds = country.federal_districts.flatMap((fd: any) => 
    fd.regions.flatMap((region: any) => region.cities.map((city: any) => city.id))
  )
  return countryCityIds.length > 0 && countryCityIds.every(id => selectedCities.value.includes(id))
}

const isFederalDistrictSelected = (fdId: number): boolean => {
  const fd = findFederalDistrictById(fdId)
  if (!fd) return false
  
  const fdCityIds = fd.regions.flatMap((region: any) => region.cities.map((city: any) => city.id))
  return fdCityIds.length > 0 && fdCityIds.every(id => selectedCities.value.includes(id))
}

const isRegionSelected = (regionId: number): boolean => {
  const region = findRegionById(regionId)
  if (!region) return false
  
  const regionCityIds = region.cities.map((city: any) => city.id)
  return regionCityIds.length > 0 && regionCityIds.every(id => selectedCities.value.includes(id))
}

// Stats functions
const getCountryStats = (country: any): string => {
  const totalCities = country.federal_districts.reduce((sum: number, fd: any) => 
    sum + fd.regions.reduce((regionSum: number, region: any) => regionSum + region.cities.length, 0), 0
  )
  return `${totalCities} городов`
}

const getFederalDistrictStats = (fd: any): string => {
  const totalCities = fd.regions.reduce((sum: number, region: any) => sum + region.cities.length, 0)
  return `${totalCities} городов`
}

// Load initial data
onMounted(async () => {
  await loadFilters()
  await loadCountriesFromNewAPI()
  await loadAllRegionsAndCities()
  await loadCitiesData()
})

// Загружаем страны из нового API
const loadCountriesFromNewAPI = async () => {
  try {
    const response = await $api.get('/v1/locations/countries')
    filterData.value.countries = response.items || []
  } catch (error) {
    console.error('Error loading countries from new API:', error)
  }
}

// Загружаем все регионы и города для дерева
const loadAllRegionsAndCities = async () => {
  try {
    // Загружаем регионы для всех стран
    const regionsPromises = filterData.value.countries.map(async (country) => {
      try {
        const response = await $api.get(`/v1/locations/regions/${country.value}`)
        return response.items || []
      } catch (error) {
        console.error(`Error loading regions for ${country.value}:`, error)
        return []
      }
    })
    
    const regionsResults = await Promise.all(regionsPromises)
    allRegions.value = regionsResults.flat()
    
    // Загружаем города для всех регионов
    const citiesPromises = allRegions.value.map(async (region) => {
      try {
        const countryCode = region.value.split('_')[0]
        const response = await $api.get(`/v1/locations/cities?country=${countryCode}&region=${region.value}`)
        return response.items || []
      } catch (error) {
        console.error(`Error loading cities for ${region.value}:`, error)
        return []
      }
    })
    
    const citiesResults = await Promise.all(citiesPromises)
    allCities.value = citiesResults.flat()
    
  } catch (error) {
    console.error('Error loading all regions and cities:', error)
  }
}
</script>

<template>
  <UCard class="mb-6">
    <!-- Advanced Mode Toggle -->
    <div class="flex justify-end mb-4">
      <UButton
        color="neutral"
        variant="ghost"
        class="flex items-center gap-2"
        @click="isAdvancedMode = !isAdvancedMode"
      >
        <span class="text-sm text-gray-500">Расширенный режим</span>
        <Icon
          :name="isAdvancedMode ? 'i-heroicons-chevron-up' : 'i-heroicons-chevron-down'"
          class="w-4 h-4 text-gray-500"
        />
      </UButton>
    </div>

    <div v-if="filtersLoading" class="flex justify-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" />
    </div>

    <div v-else-if="filtersError" class="text-red-500 text-center py-4">
      {{ filtersError }}
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Basic Filters (Always visible) -->
      <!-- Name -->
      <UFormField :label="type === 'products' ? 'Название товара' : 'Название услуги'">
        <UInput
          v-model="searchQuery"
          :placeholder="type === 'products' ? 'Введите название товара' : 'Введите название услуги'"
        />
      </UFormField>

      <!-- Price Range -->
      <UFormField label="Цена">
        <div class="flex gap-2 items-center">
          <UInput
            v-model="minPrice"
            type="number"
            placeholder="От"
            class="w-1/2"
          />
          <span>-</span>
          <UInput
            v-model="maxPrice"
            type="number"
            placeholder="До"
            class="w-1/2"
          />
        </div>
      </UFormField>

      <!-- Advanced Filters (Visible only in advanced mode) -->
      <template v-if="isAdvancedMode">
        <!-- Cities Filter Tree -->
        <div class="col-span-full">
          <UFormField label="Фильтр по городам">
            <div class="cities-filter-tree border rounded-lg p-4 max-h-96 overflow-y-auto">
              <div v-if="citiesLoading" class="flex justify-center py-4">
                <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
              </div>
              
              <div v-else-if="citiesError" class="text-red-500 text-sm py-2">
                {{ citiesError }}
              </div>
              
              <div v-else class="space-y-2">
                <div v-for="country in citiesData?.countries" :key="country.id" class="border rounded-lg">
                  <!-- Country Header -->
                  <div class="flex items-center gap-3 p-3 bg-gray-50 hover:bg-green-50 rounded-lg transition-colors">
                    <UCheckbox 
                      :model-value="isCountrySelected(country.id)"
                      @update:model-value="toggleCountrySelection(country.id)"
                    />
                    <div 
                      class="flex items-center gap-2 cursor-pointer flex-1"
                      @click="toggleCountry(country.id)"
                    >
                      <UIcon 
                        :name="expandedCountries.includes(country.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
                        class="w-4 h-4 text-gray-500"
                      />
                      <span class="font-medium text-sm">{{ country.name }}</span>
                      <span class="text-xs text-gray-500">({{ getCountryStats(country) }})</span>
                    </div>
                  </div>
                  
                  <!-- Federal Districts (only for Russia) -->
                  <div v-if="expandedCountries.includes(country.id)" class="border-t">
                    <div v-for="fd in country.federal_districts.filter(fd => fd.regions.some(region => region.cities.length > 0))" :key="fd.id" class="border-b last:border-b-0">
                      <!-- Federal District Header (only show if not default virtual district) -->
                      <div v-if="fd.id !== -1" class="flex items-center gap-3 p-2 pl-6 bg-gray-25 hover:bg-green-50 rounded-lg mx-2 my-1 transition-colors">
                        <UCheckbox 
                          :model-value="isFederalDistrictSelected(fd.id)"
                          @update:model-value="toggleFederalDistrictSelection(fd.id)"
                        />
                        <div 
                          class="flex items-center gap-2 cursor-pointer flex-1"
                          @click="toggleFederalDistrict(fd.id)"
                        >
                          <UIcon 
                            :name="expandedFederalDistricts.includes(fd.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
                            class="w-4 h-4 text-gray-500"
                          />
                          <span class="text-sm">{{ fd.name }}</span>
                          <span class="text-xs text-gray-500">({{ getFederalDistrictStats(fd) }})</span>
                        </div>
                      </div>
                      
                      <!-- Regions -->
                      <div v-if="fd.id === -1 || expandedFederalDistricts.includes(fd.id)" class="border-t">
                        <div v-for="region in fd.regions.filter(region => region.cities.length > 0)" :key="region.id" class="border-b last:border-b-0">
                          <!-- Region Header -->
                          <div class="flex items-center gap-3 p-2 pl-6 bg-white hover:bg-green-50 rounded-lg mx-2 my-1 transition-colors">
                            <UCheckbox 
                              :model-value="isRegionSelected(region.id)"
                              @update:model-value="toggleRegionSelection(region.id)"
                            />
                            <div 
                              class="flex items-center gap-2 cursor-pointer flex-1"
                              @click="toggleRegion(region.id)"
                            >
                              <UIcon 
                                :name="expandedRegions.includes(region.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
                                class="w-4 h-4 text-gray-500"
                              />
                              <span class="text-sm">{{ region.name }}</span>
                              <span class="text-xs text-gray-500">({{ region.cities.length }})</span>
                            </div>
                          </div>
                          
                          <!-- Cities -->
                          <div v-if="expandedRegions.includes(region.id)" class="border-t">
                            <div v-for="city in region.cities" :key="city.id" class="border-b last:border-b-0">
                              <div class="flex items-center gap-3 p-2 pl-10 hover:bg-green-50 rounded-lg mx-2 my-1 transition-colors">
                                <UCheckbox 
                                  :model-value="selectedCities.includes(city.id)"
                                  @update:model-value="toggleCitySelection(city.id)"
                                />
                                <div class="flex items-center gap-2 flex-1">
                                  <span class="text-sm">{{ city.name }}</span>
                                  <div class="flex gap-1">
                                    <UBadge 
                                      v-if="city.is_million_city" 
                                      size="xs" 
                                      color="blue" 
                                      variant="soft"
                                    >
                                      Миллионник
                                    </UBadge>
                                    <UBadge 
                                      v-if="city.is_regional_center" 
                                      size="xs" 
                                      color="green" 
                                      variant="soft"
                                    >
                                      Центр
                                    </UBadge>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
                    <!-- Selected Cities Summary -->
                    <div v-if="selectedCities.length > 0" class="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                      <div class="flex items-center justify-between">
                        <span class="text-sm font-medium text-green-900">
                          Выбрано городов: {{ selectedCities.length }}
                        </span>
                        <UButton 
                          size="xs" 
                          color="red" 
                          variant="ghost"
                          @click="clearAllSelections"
                        >
                          Очистить все
                        </UButton>
                      </div>
                    </div>
            </div>
          </UFormField>
        </div>

        <!-- In Stock -->
        <UFormField label="Доступность">
          <UCheckbox
            v-model="inStock"
            :label="type === 'products' ? 'В наличии' : 'Доступно'"
          />
        </UFormField>
      </template>
    </div>

    <template #footer>
      <div class="flex justify-end">
        <UButton
          color="primary"
          @click="handleSearch"
        >
          Найти
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<style scoped>
.bg-gray-25 {
  background-color: #fafafa;
}
</style> 
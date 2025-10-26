<script setup lang="ts">
import type { ProductSearchParams, ServiceSearchParams, LocationItem } from '~/types/filters'
import { isLocationItem } from '~/types/filters'
import { useProductFilters, useServiceFilters, useCompanyFilters } from '~/api/filters'
import CitiesFilterTree from './CitiesFilterTree.vue'

const props = defineProps<{
  type: 'products' | 'services' | 'companies'
  title?: string
  locationPrefix?: string
}>()

const emit = defineEmits<{
  (e: 'search', params: ProductSearchParams | ServiceSearchParams): void
}>()

// API для фильтров (оставляем только для совместимости, но не используем)
const { getProductFilters } = useProductFilters()
const { getServiceFilters } = useServiceFilters()
const { getCompanyFilters } = useCompanyFilters()

// API instance
const { $api } = useNuxtApp()

// Состояние загрузки фильтров
const filtersLoading = ref(false)
const filtersError = ref<string | null>(null)


// Search state
const searchQuery = ref('')
const selectedCities = ref<number[]>([])
const minPrice = ref<number | null>(null)
const maxPrice = ref<number | null>(null)
const inStock = ref(false)

// Cities filter data
const citiesData = ref<any>(null)
const citiesLoading = ref(false)
const citiesError = ref<string | null>(null)


// Dialog state for cities filter
const showCitiesDialog = ref(false)

// Cities filter state
const expandedCountries = ref<number[]>([])
const expandedFederalDistricts = ref<number[]>([])
const expandedRegions = ref<number[]>([])

// Computed properties

// Methods - убрали загрузку старых фильтров, используем citiesData


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

// Dialog functions
const openCitiesDialog = () => {
  showCitiesDialog.value = true
}

const closeCitiesDialog = () => {
  showCitiesDialog.value = false
}

const applyCitiesSelection = () => {
  // Сохраняем выбор
  closeCitiesDialog()
  // Автоматически применяем поиск
  handleSearch()
}

const clearCitiesSelection = () => {
  selectedCities.value = []
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
  // Суммируем количество товаров из всех федеральных округов
  const totalProducts = country.federal_districts.reduce((sum: number, fd: any) => {
    return sum + getFederalDistrictProductsCount(fd)
  }, 0)
  
  if (props.type === 'companies') {
    return `${totalProducts} компаний`
  } else {
    return `${totalProducts} товаров`
  }
}

const getFederalDistrictStats = (fd: any): string => {
  const totalProducts = getFederalDistrictProductsCount(fd)
  
  if (props.type === 'companies') {
    return `${totalProducts} компаний`
  } else {
    return `${totalProducts} товаров`
  }
}

const getRegionStats = (region: any): string => {
  // Суммируем количество товаров из всех городов в регионе
  const totalProducts = region.cities.reduce((sum: number, city: any) => {
    return sum + (city.products_count || 0)
  }, 0)
  
  if (props.type === 'companies') {
    return `${totalProducts} компаний`
  } else {
    return `${totalProducts} товаров`
  }
}

const getCityStats = (city: any): string => {
  // Используем products_count из города
  const totalProducts = city.products_count || 0
  
  if (props.type === 'companies') {
    return `${totalProducts} компаний`
  } else {
    return `${totalProducts} товаров`
  }
}

// Вспомогательная функция для подсчета товаров в федеральном округе
const getFederalDistrictProductsCount = (fd: any): number => {
  return fd.regions.reduce((sum: number, region: any) => {
    return sum + region.cities.reduce((regionSum: number, city: any) => {
      return regionSum + (city.products_count || 0)
    }, 0)
  }, 0)
}

// Load initial data
onMounted(async () => {
  await loadCitiesData()
})

</script>

<template>
  <UCard class="mb-6">
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

      <!-- Cities Filter -->
      <UFormField label="Фильтр по городам">
        <UButton 
          color="neutral" 
          variant="outline" 
          class="w-full justify-between"
          @click="openCitiesDialog"
        >
          <span>{{ selectedCities.length > 0 ? `Выбрано городов: ${selectedCities.length}` : 'Города не выбраны' }}</span>
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
        </UButton>
      </UFormField>

      <!-- In Stock -->
      <UFormField label="Доступность">
        <UCheckbox
          v-model="inStock"
          :label="type === 'products' ? 'В наличии' : 'Доступно'"
        />
      </UFormField>
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

  <!-- Cities Modal Dialog -->
  <UModal :open="showCitiesDialog" @close="closeCitiesDialog">
    <template #content>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">Выберите города</h3>
            <UButton 
              color="neutral" 
              variant="ghost" 
              icon="i-heroicons-x-mark"
              @click="closeCitiesDialog"
            />
          </div>
        </template>
        
        <div class="py-4">
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
                    <div class="flex items-center gap-3 p-2 pl-12 bg-white hover:bg-green-50 rounded-lg mx-2 my-1 transition-colors">
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
                        <span class="text-xs text-gray-500">({{ getRegionStats(region) }})</span>
                      </div>
                    </div>
                    
                    <!-- Cities -->
                    <div v-if="expandedRegions.includes(region.id)" class="border-t">
                      <div v-for="city in region.cities" :key="city.id" class="border-b last:border-b-0">
                        <div class="flex items-center gap-3 p-2 pl-16 hover:bg-green-50 rounded-lg mx-2 my-1 transition-colors">
                          <UCheckbox 
                            :model-value="selectedCities.includes(city.id)"
                            @update:model-value="toggleCitySelection(city.id)"
                          />
                          <div class="flex items-center gap-2 flex-1">
                            <span class="text-sm">{{ city.name }}</span>
                            <span class="text-xs text-gray-500">({{ getCityStats(city) }})</span>
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
      </div>
        
        <template #footer>
          <div class="space-y-3">
            <!-- Selected Cities Counter -->
            <div class="text-center">
              <span class="text-sm font-medium text-gray-700">
                Выбрано городов: 
                <span class="text-primary font-semibold">{{ selectedCities.length }}</span>
              </span>
            </div>
            
            <!-- Action Buttons -->
            <div class="flex justify-between">
              <UButton 
                color="gray" 
                variant="outline"
                @click="clearCitiesSelection"
              >
                Сброс
              </UButton>
              <UButton 
                color="primary"
                @click="applyCitiesSelection"
              >
                Выбрать
              </UButton>
            </div>
          </div>
        </template>
      </UCard>
    </template>
  </UModal>
</template>

<style scoped>
.bg-gray-25 {
  background-color: #fafafa;
}
</style> 
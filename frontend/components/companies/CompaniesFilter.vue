<script setup lang="ts">
import { useNuxtApp } from '#app'

const props = defineProps<{
  type?: 'manufacturers' | 'companies'
}>()

const emit = defineEmits<{
  (e: 'search', params: {
    search?: string
    cities?: number[]
  }): void
}>()

const { $api } = useNuxtApp()

// Search state
const searchQuery = ref('')
const selectedCities = ref<number[]>([])

// Cities filter data
const citiesData = ref<any>(null)
const citiesLoading = ref(false)
const citiesError = ref<string | null>(null)

// Modal state
const showCitiesDialog = ref(false)
const expandedCountries = ref<number[]>([])
const expandedFederalDistricts = ref<number[]>([])
const expandedRegions = ref<number[]>([])

const openCitiesDialog = () => {
  showCitiesDialog.value = true
}

const closeCitiesDialog = () => {
  showCitiesDialog.value = false
}

const clearCitiesSelection = () => {
  selectedCities.value = []
}

const applyCitiesSelection = () => {
  closeCitiesDialog()
  handleSearch()
}

// Toggle functions
const toggleCountry = (countryId: number) => {
  const index = expandedCountries.value.indexOf(countryId)
  if (index > -1) {
    expandedCountries.value.splice(index, 1)
  } else {
    expandedCountries.value.push(countryId)
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

// Check if location is selected
const isCountrySelected = (countryId: number): boolean => {
  const country = citiesData?.countries?.find((c: any) => c.id === countryId)
  if (!country) return false
  
  return country.federal_districts.every((fd: any) => 
    fd.regions.every((region: any) =>
      region.cities.every((city: any) => selectedCities.value.includes(city.id))
    )
  )
}

const isFederalDistrictSelected = (fdId: number): boolean => {
  const fd = citiesData?.countries
    ?.flatMap((c: any) => c.federal_districts)
    ?.find((fd: any) => fd.id === fdId)
  if (!fd) return false
  
  return fd.regions.every((region: any) =>
    region.cities.every((city: any) => selectedCities.value.includes(city.id))
  )
}

const isRegionSelected = (regionId: number): boolean => {
  const region = citiesData?.countries
    ?.flatMap((c: any) => c.federal_districts)
    ?.flatMap((fd: any) => fd.regions)
    ?.find((r: any) => r.id === regionId)
  if (!region) return false
  
  return region.cities.every((city: any) => selectedCities.value.includes(city.id))
}

// Toggle selection functions
const toggleCountrySelection = (countryId: number) => {
  const country = citiesData?.countries?.find((c: any) => c.id === countryId)
  if (!country) return
  
  const allCities = country.federal_districts
    .flatMap((fd: any) => fd.regions)
    .flatMap((region: any) => region.cities)
    .map((city: any) => city.id)
  
  const allSelected = allCities.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    selectedCities.value = selectedCities.value.filter(id => !allCities.includes(id))
  } else {
    selectedCities.value = [...selectedCities.value, ...allCities.filter(id => !selectedCities.value.includes(id))]
  }
}

const toggleFederalDistrictSelection = (fdId: number) => {
  const fd = citiesData?.countries
    ?.flatMap((c: any) => c.federal_districts)
    ?.find((fd: any) => fd.id === fdId)
  if (!fd) return
  
  const allCities = fd.regions
    .flatMap((region: any) => region.cities)
    .map((city: any) => city.id)
  
  const allSelected = allCities.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    selectedCities.value = selectedCities.value.filter(id => !allCities.includes(id))
  } else {
    selectedCities.value = [...selectedCities.value, ...allCities.filter(id => !selectedCities.value.includes(id))]
  }
}

const toggleRegionSelection = (regionId: number) => {
  const region = citiesData?.countries
    ?.flatMap((c: any) => c.federal_districts)
    ?.flatMap((fd: any) => fd.regions)
    ?.find((r: any) => r.id === regionId)
  if (!region) return
  
  const allCities = region.cities.map((city: any) => city.id)
  const allSelected = allCities.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    selectedCities.value = selectedCities.value.filter(id => !allCities.includes(id))
  } else {
    selectedCities.value = [...selectedCities.value, ...allCities.filter(id => !selectedCities.value.includes(id))]
  }
}

const toggleCitySelection = (cityId: number) => {
  const index = selectedCities.value.indexOf(cityId)
  if (index > -1) {
    selectedCities.value.splice(index, 1)
  } else {
    selectedCities.value.push(cityId)
  }
}

// Stats functions
const getCountryStats = (country: any): string => {
  const totalProducts = country.federal_districts.reduce((sum: number, fd: any) => {
    return sum + getFederalDistrictProductsCount(fd)
  }, 0)
  return `${totalProducts} компаний`
}

const getFederalDistrictStats = (fd: any): string => {
  const totalProducts = getFederalDistrictProductsCount(fd)
  return `${totalProducts} компаний`
}

const getRegionStats = (region: any): string => {
  const totalProducts = region.cities.reduce((sum: number, city: any) => {
    return sum + (city.products_count || 0)
  }, 0)
  return `${totalProducts} компаний`
}

const getCityStats = (city: any): string => {
  const totalProducts = city.products_count || 0
  return `${totalProducts} компаний`
}

const getFederalDistrictProductsCount = (fd: any): number => {
  return fd.regions.reduce((sum: number, region: any) => {
    return sum + region.cities.reduce((regionSum: number, city: any) => {
      return regionSum + (city.products_count || 0)
    }, 0)
  }, 0)
}

// Load cities data
const loadCitiesData = async () => {
  citiesLoading.value = true
  citiesError.value = null
  
  try {
    const response = await $api.get('/v1/cities-filter/companies')
    citiesData.value = response
  } catch (error) {
    console.error('Error loading cities data:', error)
    citiesError.value = 'Ошибка загрузки данных'
  } finally {
    citiesLoading.value = false
  }
}

// Search handler
const handleSearch = () => {
  const params: Record<string, any> = {}
  
  if (searchQuery.value) params.search = searchQuery.value
  if (selectedCities.value.length > 0) params.cities = selectedCities.value
  
  emit('search', params)
}

onMounted(async () => {
  await loadCitiesData()
  
  // Parse URL params
  const route = useRoute()
  const { cities } = route.query
  
  if (cities && typeof cities === 'string') {
    const cityIds = cities.split(',').map(id => parseInt(id)).filter(id => !isNaN(id))
    selectedCities.value = cityIds
  }
  
  if (route.query.search) {
    searchQuery.value = route.query.search as string
  }
})

</script>

<template>
  <UCard class="mb-6">
    <div v-if="false" class="flex justify-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" />
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Company Name -->
      <UFormField label="Название компании">
        <UInput
            v-model="searchQuery"
            placeholder="Введите название компании"
        />
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
                  <div class="flex items-center gap-3 p-3 bg-gray-50 hover:bg-green-50 rounded-lg">
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
                      <span class="text-sm">{{ country.name }}</span>
                      <span class="text-xs text-gray-500">({{ getCountryStats(country) }})</span>
                    </div>
                  </div>
                  
                  <!-- Federal Districts -->
                  <div v-if="expandedCountries.includes(country.id)" class="border-t">
                    <div v-for="fd in country.federal_districts.filter(fd => fd.regions.length > 0)" :key="fd.id" class="border-b last:border-b-0">
                      <!-- Federal District Header -->
                      <div class="flex items-center gap-3 p-2 pl-6 bg-white hover:bg-green-50 rounded-lg mx-2 my-1 transition-colors">
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

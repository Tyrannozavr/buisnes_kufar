<template>
  <div class="cities-filter-tree">
    <div v-if="loading" class="flex justify-center py-4">
      <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
    </div>
    
    <div v-else-if="error" class="text-red-500 text-sm py-2">
      {{ error }}
    </div>
    
    <div v-else class="space-y-2 max-h-96 overflow-y-auto">
      <div v-for="country in locationTree.countries" :key="country.id" class="border rounded-lg">
        <!-- Country Header -->
        <div 
          class="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 cursor-pointer"
          @click="toggleCountry(country.id)"
        >
          <div class="flex items-center gap-2">
            <UIcon 
              :name="expandedCountries.has(country.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
              class="w-4 h-4 text-gray-500"
            />
            <span class="font-medium text-sm">{{ country.name }}</span>
            <span class="text-xs text-gray-500">({{ getCountryStats(country) }})</span>
          </div>
          <UCheckbox 
            :model-value="isCountrySelected(country.id)"
            @update:model-value="toggleCountrySelection(country.id)"
            @click.stop
          />
        </div>
        
        <!-- Federal Districts (only for Russia) -->
        <div v-if="expandedCountries.has(country.id)" class="border-t">
          <div v-for="fd in country.federal_districts" :key="fd.id" class="border-b last:border-b-0">
            <!-- Federal District Header -->
            <div 
              class="flex items-center justify-between p-2 pl-6 bg-gray-25 hover:bg-gray-50 cursor-pointer"
              @click="toggleFederalDistrict(fd.id)"
            >
              <div class="flex items-center gap-2">
                <UIcon 
                  :name="expandedFederalDistricts.has(fd.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
                  class="w-4 h-4 text-gray-500"
                />
                <span class="text-sm">{{ fd.name }}</span>
                <span class="text-xs text-gray-500">({{ getFederalDistrictStats(fd) }})</span>
              </div>
              <UCheckbox 
                :model-value="isFederalDistrictSelected(fd.id)"
                @update:model-value="toggleFederalDistrictSelection(fd.id)"
                @click.stop
              />
            </div>
            
            <!-- Regions -->
            <div v-if="expandedFederalDistricts.has(fd.id)" class="border-t">
              <div v-for="region in fd.regions" :key="region.id" class="border-b last:border-b-0">
                <!-- Region Header -->
                <div 
                  class="flex items-center justify-between p-2 pl-10 bg-white hover:bg-gray-25 cursor-pointer"
                  @click="toggleRegion(region.id)"
                >
                  <div class="flex items-center gap-2">
                    <UIcon 
                      :name="expandedRegions.has(region.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
                      class="w-4 h-4 text-gray-500"
                    />
                    <span class="text-sm">{{ region.name }}</span>
                    <span class="text-xs text-gray-500">({{ region.cities.length }})</span>
                  </div>
                  <UCheckbox 
                    :model-value="isRegionSelected(region.id)"
                    @update:model-value="toggleRegionSelection(region.id)"
                    @click.stop
                  />
                </div>
                
                <!-- Cities -->
                <div v-if="expandedRegions.has(region.id)" class="border-t">
                  <div v-for="city in region.cities" :key="city.id" class="border-b last:border-b-0">
                    <div class="flex items-center justify-between p-2 pl-14 hover:bg-gray-25">
                      <div class="flex items-center gap-2">
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
                      <UCheckbox 
                        :model-value="selectedCities.includes(city.id)"
                        @update:model-value="toggleCitySelection(city.id)"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Direct Regions (for non-Russia countries) -->
        <div v-else-if="expandedCountries.has(country.id) && country.federal_districts.length === 0" class="border-t">
          <div v-for="region in country.regions" :key="region.id" class="border-b last:border-b-0">
            <!-- Region Header -->
            <div 
              class="flex items-center justify-between p-2 pl-6 bg-gray-25 hover:bg-gray-50 cursor-pointer"
              @click="toggleRegion(region.id)"
            >
              <div class="flex items-center gap-2">
                <UIcon 
                  :name="expandedRegions.has(region.id) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" 
                  class="w-4 h-4 text-gray-500"
                />
                <span class="text-sm">{{ region.name }}</span>
                <span class="text-xs text-gray-500">({{ region.cities.length }})</span>
              </div>
              <UCheckbox 
                :model-value="isRegionSelected(region.id)"
                @update:model-value="toggleRegionSelection(region.id)"
                @click.stop
              />
            </div>
            
            <!-- Cities -->
            <div v-if="expandedRegions.has(region.id)" class="border-t">
              <div v-for="city in region.cities" :key="city.id" class="border-b last:border-b-0">
                <div class="flex items-center justify-between p-2 pl-10 hover:bg-gray-25">
                  <div class="flex items-center gap-2">
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
                  <UCheckbox 
                    :model-value="selectedCities.includes(city.id)"
                    @update:model-value="toggleCitySelection(city.id)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Selected Cities Summary -->
    <div v-if="selectedCities.length > 0" class="mt-4 p-3 bg-blue-50 rounded-lg">
      <div class="flex items-center justify-between">
        <span class="text-sm font-medium text-blue-900">
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
</template>

<script setup lang="ts">
interface City {
  id: number
  name: string
  population: number
  is_million_city: boolean
  is_regional_center: boolean
}

interface Region {
  id: number
  name: string
  code: string
  cities: City[]
}

interface FederalDistrict {
  id: number
  name: string
  code: string
  regions: Region[]
}

interface Country {
  id: number
  code: string
  name: string
  federal_districts: FederalDistrict[]
  regions?: Region[] // For non-Russia countries
}

interface LocationTreeResponse {
  countries: Country[]
  total_countries: number
  total_federal_districts: number
  total_regions: number
  total_cities: number
}

const props = defineProps<{
  modelValue: number[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number[]): void
}>()

const { $api } = useNuxtApp()

// Reactive state
const locationTree = ref<LocationTreeResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Selection state
const selectedCities = ref<number[]>(props.modelValue || [])
const expandedCountries = ref(new Set<number>())
const expandedFederalDistricts = ref(new Set<number>())
const expandedRegions = ref(new Set<number>())

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  selectedCities.value = newValue || []
})

// Watch for internal changes
watch(selectedCities, (newValue) => {
  emit('update:modelValue', newValue)
})

// Fetch location tree
const fetchLocationTree = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await $api.get('/v1/cities-filter/cities-filter')
    locationTree.value = response
  } catch (e) {
    error.value = 'Ошибка загрузки данных о городах'
    console.error('Error fetching location tree:', e)
  } finally {
    loading.value = false
  }
}

// Toggle functions
const toggleCountry = (countryId: number) => {
  if (expandedCountries.value.has(countryId)) {
    expandedCountries.value.delete(countryId)
  } else {
    expandedCountries.value.add(countryId)
  }
}

const toggleFederalDistrict = (fdId: number) => {
  if (expandedFederalDistricts.value.has(fdId)) {
    expandedFederalDistricts.value.delete(fdId)
  } else {
    expandedFederalDistricts.value.add(fdId)
  }
}

const toggleRegion = (regionId: number) => {
  if (expandedRegions.value.has(regionId)) {
    expandedRegions.value.delete(regionId)
  } else {
    expandedRegions.value.add(regionId)
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
  
  const regionCityIds = region.cities.map(city => city.id)
  const allSelected = regionCityIds.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    // Deselect all cities in region
    selectedCities.value = selectedCities.value.filter(id => !regionCityIds.includes(id))
  } else {
    // Select all cities in region
    const newSelections = regionCityIds.filter(id => !selectedCities.value.includes(id))
    selectedCities.value = [...selectedCities.value, ...newSelections]
  }
}

const toggleFederalDistrictSelection = (fdId: number) => {
  const fd = findFederalDistrictById(fdId)
  if (!fd) return
  
  const fdCityIds = fd.regions.flatMap(region => region.cities.map(city => city.id))
  const allSelected = fdCityIds.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    // Deselect all cities in federal district
    selectedCities.value = selectedCities.value.filter(id => !fdCityIds.includes(id))
  } else {
    // Select all cities in federal district
    const newSelections = fdCityIds.filter(id => !selectedCities.value.includes(id))
    selectedCities.value = [...selectedCities.value, ...newSelections]
  }
}

const toggleCountrySelection = (countryId: number) => {
  const country = findCountryById(countryId)
  if (!country) return
  
  const countryCityIds = country.federal_districts.flatMap(fd => 
    fd.regions.flatMap(region => region.cities.map(city => city.id))
  )
  const allSelected = countryCityIds.every(id => selectedCities.value.includes(id))
  
  if (allSelected) {
    // Deselect all cities in country
    selectedCities.value = selectedCities.value.filter(id => !countryCityIds.includes(id))
  } else {
    // Select all cities in country
    const newSelections = countryCityIds.filter(id => !selectedCities.value.includes(id))
    selectedCities.value = [...selectedCities.value, ...newSelections]
  }
}

const clearAllSelections = () => {
  selectedCities.value = []
}

// Helper functions
const findCountryById = (id: number): Country | null => {
  return locationTree.value?.countries.find(c => c.id === id) || null
}

const findFederalDistrictById = (id: number): FederalDistrict | null => {
  for (const country of locationTree.value?.countries || []) {
    const fd = country.federal_districts.find(fd => fd.id === id)
    if (fd) return fd
  }
  return null
}

const findRegionById = (id: number): Region | null => {
  for (const country of locationTree.value?.countries || []) {
    for (const fd of country.federal_districts) {
      const region = fd.regions.find(r => r.id === id)
      if (region) return region
    }
  }
  return null
}

// Check selection state
const isCountrySelected = (countryId: number): boolean => {
  const country = findCountryById(countryId)
  if (!country) return false
  
  const countryCityIds = country.federal_districts.flatMap(fd => 
    fd.regions.flatMap(region => region.cities.map(city => city.id))
  )
  return countryCityIds.length > 0 && countryCityIds.every(id => selectedCities.value.includes(id))
}

const isFederalDistrictSelected = (fdId: number): boolean => {
  const fd = findFederalDistrictById(fdId)
  if (!fd) return false
  
  const fdCityIds = fd.regions.flatMap(region => region.cities.map(city => city.id))
  return fdCityIds.length > 0 && fdCityIds.every(id => selectedCities.value.includes(id))
}

const isRegionSelected = (regionId: number): boolean => {
  const region = findRegionById(regionId)
  if (!region) return false
  
  const regionCityIds = region.cities.map(city => city.id)
  return regionCityIds.length > 0 && regionCityIds.every(id => selectedCities.value.includes(id))
}

// Stats functions
const getCountryStats = (country: Country): string => {
  const totalCities = country.federal_districts.reduce((sum, fd) => 
    sum + fd.regions.reduce((regionSum, region) => regionSum + region.cities.length, 0), 0
  )
  return `${totalCities} городов`
}

const getFederalDistrictStats = (fd: FederalDistrict): string => {
  const totalCities = fd.regions.reduce((sum, region) => sum + region.cities.length, 0)
  return `${totalCities} городов`
}

// Initialize
onMounted(() => {
  fetchLocationTree()
})
</script>

<style scoped>
.cities-filter-tree {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.bg-gray-25 {
  background-color: #fafafa;
}
</style>

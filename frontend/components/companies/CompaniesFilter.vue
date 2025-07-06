<script setup lang="ts">
import type {LocationItem} from '~/types/location'
import {useCompanyFilters} from '~/api/filters'

const emit = defineEmits<{
  (e: 'search', params: {
    search?: string
    country?: string
    federalDistrict?: string
    region?: string
    city?: string
  }): void
}>()

// API для фильтров
const { getCompanyFilters } = useCompanyFilters()

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

// Search state
const searchQuery = ref('')
const selectedCountry = ref<LocationItem | undefined>(undefined)
const selectedFederalDistrict = ref<LocationItem | undefined>(undefined)
const selectedRegion = ref<LocationItem | undefined>(undefined)
const selectedCity = ref<LocationItem | undefined>(undefined)

const isSelectedCountry = computed(() => selectedCountry.value !== undefined)

// Computed properties
const isRussia = computed(() => selectedCountry.value?.value === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Фильтрация городов по региону
const filteredCities = computed(() => {
  if (!selectedRegion.value) return []
  return filterData.value.cities.filter(city => city.label.includes(selectedRegion.value!.value) || city.value.includes(selectedRegion.value!.value))
})

// Methods
const loadFilters = async () => {
  filtersLoading.value = true
  filtersError.value = null
  
  try {
    const response = await getCompanyFilters()
    
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

const handleCountryChange = async (country: LocationItem) => {
  selectedCountry.value = country
  selectedFederalDistrict.value = undefined
  selectedRegion.value = undefined
  selectedCity.value = undefined
}

const handleFederalDistrictChange = async (district: LocationItem) => {
  selectedFederalDistrict.value = district
  selectedRegion.value = undefined
  selectedCity.value = undefined
}

const handleRegionChange = async (region: LocationItem) => {
  selectedRegion.value = region
  selectedCity.value = undefined
}

const handleSearch = () => {
  const params: Record<string, string> = {}

  if (searchQuery.value) params.search = searchQuery.value
  if (selectedCountry.value) params.country = selectedCountry.value.value
  if (selectedFederalDistrict.value) params.federalDistrict = selectedFederalDistrict.value.value
  if (selectedRegion.value) params.region = selectedRegion.value.value
  if (selectedCity.value) params.city = selectedCity.value.value

  emit('search', params)
}

// Load initial data
onMounted(() => {
  loadFilters()
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
      <!-- Company Name -->
      <UFormField label="Название компании">
        <UInput
            v-model="searchQuery"
            placeholder="Введите название компании"
        />
      </UFormField>
      <UFormField label="Страна">
        <USelectMenu
            v-model="selectedCountry"
            :items="filterData.countries"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите страну"
            searchable
            @update:model-value="handleCountryChange"
        />
      </UFormField>
      <!-- Federal District (only for Russia) -->
      <UFormField
          v-if="showFederalDistricts"
          label="Федеральный округ"
      >
        <USelectMenu
            v-model="selectedFederalDistrict"
            :items="filterData.federal_districts"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите федеральный округ"
            searchable
            @update:model-value="handleFederalDistrictChange"
        />
      </UFormField>
      <!-- Region -->
      <UFormField label="Регион">
        <USelectMenu
            v-model="selectedRegion"
            :items="filterData.regions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите регион"
            searchable
            @update:model-value="handleRegionChange"
        />
      </UFormField>

      <!-- City -->
      <UFormField label="Город">
        <USelectMenu
            v-model="selectedCity"
            :items="filteredCities"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите город"
            searchable
            :disabled="!selectedRegion"
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
</template>
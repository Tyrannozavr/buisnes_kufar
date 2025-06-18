<script setup lang="ts">
import type {LocationItem} from '~/types/location'
import {useCompaniesLocations} from '~/api/companies-locations'

const emit = defineEmits<{
  (e: 'search', params: {
    search?: string
    country?: string
    federalDistrict?: string
    region?: string
    city?: string
    product?: string
  }): void
}>()

// API
const {
  countryOptions,
  federalDistrictOptions,
  regionOptions,
  cityOptions,
  countriesLoading,
  federalDistrictsLoading,
  regionsLoading,
  citiesLoading,
  countriesError,
  federalDistrictsError,
  regionsError,
  citiesError,
  loadFederalDistricts,
  loadRegions,
  loadCities
} = useCompaniesLocations('companies')

// Search state
const searchQuery = ref('')
const selectedCountry = ref<LocationItem | undefined>(undefined)
const selectedFederalDistrict = ref<LocationItem | undefined>(undefined)
const selectedRegion = ref<LocationItem | undefined>(undefined)
const selectedCity = ref<LocationItem | undefined>(undefined)
const productQuery = ref('')

const isSelectedCountry = computed(() => selectedCountry.value !== undefined)

// Computed properties
const isRussia = computed(() => selectedCountry.value?.value === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Methods
const loadLocations = async () => {
  if (isRussia.value && !federalDistrictOptions.value.length) {
    await loadFederalDistricts()
  }
  if (selectedCountry.value && !regionOptions.value.length) {
    await loadRegions(selectedCountry.value.value, selectedFederalDistrict.value?.value)
  }
  if (selectedCountry.value && selectedRegion.value && !cityOptions.value.length) {
    await loadCities(selectedCountry.value.value, selectedRegion.value.value)
  }
}

const handleCountryChange = async (country: LocationItem) => {
  selectedCountry.value = country
  selectedFederalDistrict.value = undefined
  selectedRegion.value = undefined
  selectedCity.value = undefined
  await loadLocations()
}

const handleFederalDistrictChange = async (district: LocationItem) => {
  selectedFederalDistrict.value = district
  selectedRegion.value = undefined
  selectedCity.value = undefined
  await loadLocations()
}

const handleRegionChange = async (region: LocationItem) => {
  selectedRegion.value = region
  selectedCity.value = undefined
  await loadLocations()
}

const handleSearch = () => {
  const params: Record<string, string> = {}

  if (searchQuery.value) params.search = searchQuery.value
  if (selectedCountry.value) params.country = selectedCountry.value.value
  if (selectedFederalDistrict.value) params.federalDistrict = selectedFederalDistrict.value.value
  if (selectedRegion.value) params.region = selectedRegion.value.value
  if (selectedCity.value) params.city = selectedCity.value.value
  if (productQuery.value) params.product = productQuery.value

  emit('search', params)
}

// Load initial data
loadLocations()
</script>

<template>
  <UCard class="mb-6">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
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
            :items="countryOptions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите страну"
            searchable
            :loading="countriesLoading"
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
            :items="federalDistrictOptions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите федеральный округ"
            searchable
            :loading="federalDistrictsLoading"
            @update:model-value="handleFederalDistrictChange"
        />
      </UFormField>
      <!-- Region -->
      <UFormField label="Регион">
        <USelectMenu
            v-model="selectedRegion"
            :items="regionOptions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите регион"
            searchable
            :loading="regionsLoading"
            @update:model-value="handleRegionChange"
        />
      </UFormField>

      <!-- City -->
      <UFormField label="Город">
        <USelectMenu
            v-model="selectedCity"
            :items="cityOptions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите город"
            searchable
            :disabled="!isSelectedCountry"
            :loading="citiesLoading"
        />
      </UFormField>

      <!-- Product -->
      <UFormField label="Продукция">
        <UInput
            v-model="productQuery"
            placeholder="Введите название продукции"
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
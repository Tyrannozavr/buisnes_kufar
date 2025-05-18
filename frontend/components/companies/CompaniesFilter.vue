<script setup lang="ts">
import type {Region, City, FederalDistrict} from '~/types/location'
import {useLocationsApi} from '~/api/locations'
import type {FilterItem} from "~/types/Filter";

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
const {getCountries, getFederalDistricts, getRegions, getCities} = useLocationsApi()

// Search state
const searchQuery = ref('')
const selectedCountry = ref<string | null>(null)
const selectedFederalDistrict = ref<string | null>(null)
const selectedRegion = ref<string | null>(null)
const selectedCity = ref<string | null>(null)
const productQuery = ref('')

// Loading states
const loadingCountries = ref(true)
const loadingFederalDistricts = ref(false)
const loadingRegions = ref(false)
const loadingCities = ref(false)


const isSelectedCountry = computed(() => selectedCountry.value!== null)
// Location data
const {data: countries} = await getCountries()
loadingCountries.value = false

const federalDistricts = ref<FederalDistrict[]>([])
const regions = ref<Region[]>([])
const cities = ref<City[]>([])

// Computed properties
const isRussia = computed(() => selectedCountry.value === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Methods
const loadLocations = async () => {
  if (isRussia.value && !federalDistricts.value.length) {
    loadingFederalDistricts.value = true
    const {data} = await getFederalDistricts()
    federalDistricts.value = data.value ?? []
    loadingFederalDistricts.value = false
  }
  if (!regions.value.length) {
    loadingRegions.value = true
    const {data} = await getRegions(selectedCountry.value || "", selectedFederalDistrict.value || undefined)
    regions.value = data.value ?? []
    loadingRegions.value = false
  }
  if (!cities.value.length) {
    loadingCities.value = true
    const {data} = await getCities(selectedCountry.value || "")
    cities.value = data.value ?? []
    loadingCities.value = false
  }
}

const handleCountryChange = async (country: FilterItem) => {
  selectedCountry.value = country.value
  await loadLocations()
}

const handleFederalDistrictChange = async (district: FilterItem) => {
  selectedFederalDistrict.value = district.value
  await loadLocations()
}

const handleRegionChange = async (region: FilterItem) => {
  selectedRegion.value = region.value
  await loadLocations()
}

const handleSearch = () => {
  const params: Record<string, string> = {}

  if (searchQuery.value) params.search = searchQuery.value
  if (selectedCountry.value) params.country = selectedCountry.value
  if (selectedFederalDistrict.value) params.federalDistrict = selectedFederalDistrict.value
  if (selectedRegion.value) params.region = selectedRegion.value
  if (selectedCity.value) params.city = selectedCity.value
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
            :items="countries ?? []"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите страну"
            searchable
            :loading="loadingCountries"
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
            :items="federalDistricts"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите федеральный округ"
            searchable
            :loading="loadingFederalDistricts"
            @update:model-value="handleFederalDistrictChange"
        />
      </UFormField>
      <!-- Region -->
      <UFormField label="Регион">
        <USelectMenu
            v-model="selectedRegion"
            :items="regions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите регион"
            searchable
            :loading="loadingRegions"
            @update:model-value="handleRegionChange"
        />
      </UFormField>

      <!-- City -->
      <UFormField label="Город">
        <USelectMenu
            v-model="selectedCity"
            :items="cities"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите город"
            searchable
            :disabled="!isSelectedCountry"
            :loading="loadingCities"
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
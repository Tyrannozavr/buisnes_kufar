<script setup lang="ts">
import type { Company } from '~/types/company'
import type { Country, Region, City, FederalDistrict } from '~/types/location'
import { useLocationsApi } from '~/api/locations'
import { useManufacturersApi } from '~/api/manufacturers'

const route = useRoute()
const title = ref('Производители товаров')
const description = ref('Список производителей товаров.')

// Success message handling
const showSuccessMessage = ref(false)
const successMessage = ref('')

// API
const { getCountries, getFederalDistricts, getRegions, getCities } = useLocationsApi()
const { searchManufacturers } = useManufacturersApi()

// Search state
const searchQuery = ref('')
const selectedCountry = ref<string | null>(null)
const selectedFederalDistrict = ref<string | null>(null)
const selectedRegion = ref<string | null>(null)
const selectedCity = ref<string | null>(null)
const productQuery = ref('')

// Location data
const { data: countries } = await getCountries()
const federalDistricts = ref<FederalDistrict[]>([])
const regions = ref<Region[]>([])
const cities = ref<City[]>([])

// Manufacturers data
const manufacturers = ref<Company[]>([])
const manufacturersPending = ref(false)
const manufacturersError = ref<Error | null>(null)

// Computed properties
const isRussia = computed(() => selectedCountry.value === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Methods
const handleCountryChange = async (countryId: string) => {
  selectedCountry.value = countryId
  selectedFederalDistrict.value = null
  selectedRegion.value = null
  selectedCity.value = null
  federalDistricts.value = []
  regions.value = []
  cities.value = []

  if (countryId === 'Россия') {
    const { data } = await getFederalDistricts(countryId)
    federalDistricts.value = data.value ?? []
  }
}

const handleFederalDistrictChange = async (districtId: string) => {
  selectedFederalDistrict.value = districtId
  selectedRegion.value = null
  selectedCity.value = null
  regions.value = []
  cities.value = []

  if (districtId) {
    const { data } = await getRegions(selectedCountry.value!, districtId)
    regions.value = data.value ?? []
  }
}

const handleRegionChange = async (regionId: string) => {
  selectedRegion.value = regionId
  selectedCity.value = null
  cities.value = []

  if (regionId) {
    const { data } = await getCities(selectedCountry.value!)
    cities.value = data.value ?? []
  }
}

const handleSearch = async (params: {
  search?: string
  country?: string
  federalDistrict?: string
  region?: string
  city?: string
  product?: string
}) => {
  manufacturersPending.value = true
  manufacturersError.value = null

  try {
    const { data } = await searchManufacturers(params)
    manufacturers.value = data.value ?? []
  } catch (error) {
    console.error('Search error:', error)
    manufacturersError.value = error as Error
  } finally {
    manufacturersPending.value = false
  }
}

// Initial data loading during SSR
const initialSearchParams = {
  search: route.query.search as string,
  country: route.query.country as string,
  federalDistrict: route.query.federalDistrict as string,
  region: route.query.region as string,
  city: route.query.city as string,
  product: route.query.product as string
}

// Set initial values from route query
if (initialSearchParams.country) {
  selectedCountry.value = initialSearchParams.country
  if (initialSearchParams.country === 'Россия') {
    const { data } = await getFederalDistricts(initialSearchParams.country)
    federalDistricts.value = data.value ?? []
  }
}

if (initialSearchParams.federalDistrict) {
  selectedFederalDistrict.value = initialSearchParams.federalDistrict
  if (selectedCountry.value) {
    const { data } = await getRegions(selectedCountry.value, initialSearchParams.federalDistrict)
    regions.value = data.value ?? []
  }
}

if (initialSearchParams.region) {
  selectedRegion.value = initialSearchParams.region
  if (selectedCountry.value) {
    const { data } = await getCities(selectedCountry.value)
    cities.value = data.value ?? []
  }
}

// Initial manufacturers load
const { data: initialManufacturers } = await searchManufacturers(initialSearchParams)
manufacturers.value = initialManufacturers.value ?? []

// Check if there's a success message in the query parameters
if (route.query.created === 'true') {
  successMessage.value = 'Производитель успешно добавлен'
  showSuccessMessage.value = true

  // Auto-hide the message after 5 seconds
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 5000)
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Success message notification -->
    <div v-if="showSuccessMessage" class="mb-6">
      <UAlert
        variant="solid"
        color="success"
        title="Успешно!"
        :description="successMessage"
        class="mb-4"
        icon="i-heroicons-check-circle"
      >
        <template #footer>
          <div class="flex justify-end">
            <UButton
              color="neutral"
              variant="ghost"
              size="sm"
              @click="showSuccessMessage = false"
            >
              Закрыть
            </UButton>
          </div>
        </template>
      </UAlert>
    </div>

    <h1 class="text-2xl font-bold mb-4">{{ title }}</h1>
    <p class="mb-6">{{ description }}</p>

    <!-- Search Form -->
    <ManufacturersFilter @search="handleSearch" />
    <!-- Manufacturers List -->
    <ManufacturersList
      :manufacturers="manufacturers"
      :pending="manufacturersPending"
      :error="manufacturersError"
    />
  </div>
</template>

<style scoped>
/* Custom styles can be added here */
</style>
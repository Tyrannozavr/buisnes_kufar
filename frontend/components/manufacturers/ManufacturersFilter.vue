<script setup lang="ts">
import type { Region, City, FederalDistrict } from '~/types/location'
import { useLocationsApi } from '~/api/locations'

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
const { getCountries, getFederalDistricts, getRegions, getCities } = useLocationsApi()

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

// Computed properties
const isRussia = computed(() => selectedCountry.value === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Methods
const handleCountryChange = async (country: string) => {
  selectedCountry.value = country
  selectedFederalDistrict.value = null
  selectedRegion.value = null
  selectedCity.value = null
  federalDistricts.value = []
  regions.value = []
  cities.value = []

  if (country) {
    const [federalDistrictsResponse, regionsResponse] = await Promise.all([
      getFederalDistricts(country),
      isRussia.value ? null : getRegions(country)
    ])

    federalDistricts.value = federalDistrictsResponse.data.value ?? []

    if (!isRussia.value && regionsResponse) {
      regions.value = regionsResponse.data.value ?? []
    }
  }
}

const handleFederalDistrictChange = async (districtId: string) => {
  selectedFederalDistrict.value = districtId
  selectedRegion.value = null
  selectedCity.value = null
  regions.value = []
  cities.value = []

  if (districtId) {
    const { data } = await getRegions(districtId)
    regions.value = data.value ?? []
  }
}

const handleRegionChange = async (regionId: string) => {
  selectedRegion.value = regionId
  selectedCity.value = null
  cities.value = []

  if (regionId) {
    const { data } = await getCities(regionId)
    cities.value = data.value ?? []
  }
}

const handleSearch = () => {
  const params: Record<string, string> = {}
  
  if (searchQuery.value) {
    params.search = searchQuery.value
  }
  if (selectedCountry.value) {
    params.country = selectedCountry.value
  }
  if (selectedFederalDistrict.value) {
    params.federalDistrict = selectedFederalDistrict.value
  }
  if (selectedRegion.value) {
    params.region = selectedRegion.value
  }
  if (selectedCity.value) {
    params.city = selectedCity.value
  }
  if (productQuery.value) {
    params.product = productQuery.value
  }

  emit('search', params)
}
</script>

<template>
  <UCard class="mb-6">
    <template #header>
      <h2 class="text-xl font-semibold">Поиск производителей</h2>
    </template>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Company Name -->
      <UFormField label="Название компании">
        <UInput
          v-model="searchQuery"
          placeholder="Введите название компании"
        />
      </UFormField>
      <!-- Country -->
      <UFormField label="Страна">
        <USelect
          v-model="selectedCountry"
          :items="countries ?? []"
          placeholder="Выберите страну"
          @update:model-value="handleCountryChange"
        />
      </UFormField>
      <!-- Federal District (only for Russia) -->
      <UFormField
        v-if="showFederalDistricts"
        label="Федеральный округ"
      >
        <USelect
          v-model="selectedFederalDistrict"
          :items="federalDistricts"
          placeholder="Выберите федеральный округ"
          @update:model-value="handleFederalDistrictChange"
        />
      </UFormField>
      <!-- Region -->
      <UFormField label="Регион">
        <USelect
          v-model="selectedRegion"
          :items="regions"
          placeholder="Выберите регион"
          @update:model-value="handleRegionChange"
        />
      </UFormField>

      <!-- City -->
      <UFormField label="Город">
        <USelect
          v-model="selectedCity"
          :items="cities"
          placeholder="Выберите город"
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
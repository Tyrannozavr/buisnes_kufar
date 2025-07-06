<script setup lang="ts">
import type { ProductSearchParams, ServiceSearchParams, LocationItem } from '~/types/filters'
import { isLocationItem } from '~/types/filters'
import { useProductFilters, useServiceFilters } from '~/api/filters'

const props = defineProps<{
  type: 'products' | 'services'
  title: string
  locationPrefix?: string
}>()

const emit = defineEmits<{
  (e: 'search', params: ProductSearchParams | ServiceSearchParams): void
}>()

// API для фильтров
const { getProductFilters } = useProductFilters()
const { getServiceFilters } = useServiceFilters()

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
const minPrice = ref<number | null>(null)
const maxPrice = ref<number | null>(null)
const inStock = ref(false)

// Filter mode
const isAdvancedMode = ref(false)

// Computed properties
const isRussia = computed(() => selectedCountry.value?.value === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Фильтрация городов по региону
const filteredCities = computed(() => {
  if (!selectedRegion.value) return []
  // Фильтруем города по региону, если value совпадает с value региона в названии города (можно доработать под вашу структуру)
  // Например, если города имеют value вида "Минск, Минская область", фильтруем по includes
  return filterData.value.cities.filter(city => city.label.includes(selectedRegion.value!.value) || city.value.includes(selectedRegion.value!.value))
})

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
  const params = {
    search: searchQuery.value,
    country: selectedCountry.value?.value || '',
    federalDistrict: selectedFederalDistrict.value?.value || '',
    region: selectedRegion.value?.value || '',
    city: selectedCity.value?.value || '',
    minPrice: minPrice.value || undefined,
    maxPrice: maxPrice.value || undefined,
    inStock: inStock.value || undefined
  }

  emit('search', params)
}

// Load initial data
onMounted(() => {
  loadFilters()
})
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
        <!-- Country -->
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
            placeholder="Выберите город"
            :disabled="!selectedRegion"
          />
        </UFormField>

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
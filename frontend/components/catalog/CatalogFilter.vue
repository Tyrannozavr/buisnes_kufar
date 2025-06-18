<script setup lang="ts">
import { useCompaniesLocations } from '~/api/companies-locations'
import type { ProductSearchParams, ServiceSearchParams, ProductType, ServiceType, LocationItem } from '~/types/filters'
import { isLocationItem } from '~/types/filters'

const props = defineProps<{
  type: 'products' | 'services'
  title: string
  locationPrefix?: string
}>()

const emit = defineEmits<{
  (e: 'search', params: ProductSearchParams | ServiceSearchParams): void
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
} = useCompaniesLocations(props.locationPrefix)

// Search state
const searchQuery = ref('')
const selectedCountry = ref<LocationItem | undefined>(undefined)
const selectedFederalDistrict = ref<LocationItem | undefined>(undefined)
const selectedRegion = ref<LocationItem | undefined>(undefined)
const selectedCity = ref<LocationItem | undefined>(undefined)
const selectedType = ref<ProductType | ServiceType | undefined>(undefined)
const minPrice = ref<number | null>(null)
const maxPrice = ref<number | null>(null)
const inStock = ref(false)

// Filter mode
const isAdvancedMode = ref(false)

// Types based on filter type
const productTypes: ProductType[] = [
  { label: 'Строительные материалы', value: 'construction' },
  { label: 'Инструменты', value: 'tools' },
  { label: 'Оборудование', value: 'equipment' },
  { label: 'Расходные материалы', value: 'consumables' },
  { label: 'Сантехника', value: 'plumbing' },
  { label: 'Электрика', value: 'electrical' },
  { label: 'Отделочные материалы', value: 'finishing' },
  { label: 'Прочее', value: 'other' }
]

const serviceTypes: ServiceType[] = [
  { label: 'Строительные услуги', value: 'construction' },
  { label: 'Ремонтные работы', value: 'repair' },
  { label: 'Монтажные работы', value: 'installation' },
  { label: 'Отделочные работы', value: 'finishing' },
  { label: 'Проектирование', value: 'design' },
  { label: 'Консультации', value: 'consultation' },
  { label: 'Прочее', value: 'other' }
]

const types = computed(() => props.type === 'products' ? productTypes : serviceTypes)

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
  const params = {
    search: searchQuery.value,
    country: selectedCountry.value?.value || '',
    federalDistrict: selectedFederalDistrict.value?.value || '',
    region: selectedRegion.value?.value || '',
    city: selectedCity.value?.value || '',
    type: selectedType.value?.value || '',
    minPrice: minPrice.value || undefined,
    maxPrice: maxPrice.value || undefined,
    inStock: inStock.value || undefined
  }

  emit('search', params)
}

// Load initial data
loadLocations()
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

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <!-- Basic Filters (Always visible) -->
      <!-- Name -->
      <UFormField :label="type === 'products' ? 'Название товара' : 'Название услуги'">
        <UInput
          v-model="searchQuery"
          :placeholder="type === 'products' ? 'Введите название товара' : 'Введите название услуги'"
        />
      </UFormField>

      <!-- Type -->
      <UFormField :label="type === 'products' ? 'Тип товара' : 'Тип услуги'">
        <USelectMenu
          v-model="selectedType"
          :items="types"
          :search-input="{
            placeholder: 'Поиск',
            icon: 'i-lucide-search'
          }"
          :placeholder="type === 'products' ? 'Выберите тип товара' : 'Выберите тип услуги'"
          searchable
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

        <!-- City (простой выпадающий список без поиска) -->
        <UFormField label="Город">
          <USelectMenu
            v-model="selectedCity"
            :items="cityOptions"
            placeholder="Выберите город"
            :disabled="!selectedCountry"
            :loading="citiesLoading"
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
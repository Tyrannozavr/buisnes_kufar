<script setup lang="ts">
import { useLocationsApi } from '~/api/locations'

interface LocationItem {
  label: string
  value: string
}

const props = defineProps<{
  modelValue: {
    name: string
    country: string
    federalDistrict: string
    region: string
    city: string
  }
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: typeof props.modelValue): void
  (e: 'search', value: typeof props.modelValue): void
}>()

// API
const { getCountries, getFederalDistricts, getRegions, getCities } = useLocationsApi()

// Loading states
const loadingCountries = ref(true)
const loadingFederalDistricts = ref(false)
const loadingRegions = ref(false)
const loadingCities = ref(false)

// Location data
const { data: countries } = await getCountries()
loadingCountries.value = false

const federalDistricts = ref<LocationItem[]>([])
const regions = ref<LocationItem[]>([])
const cities = ref<LocationItem[]>([])

// Computed properties
const isRussia = computed(() => props.modelValue.country === 'Россия')
const showFederalDistricts = computed(() => isRussia.value)

// Methods
const loadLocations = async () => {
  if (isRussia.value && !federalDistricts.value.length) {
    loadingFederalDistricts.value = true
    const { data } = await getFederalDistricts()
    federalDistricts.value = data.value ?? []
    loadingFederalDistricts.value = false
  }
  if (!regions.value.length) {
    loadingRegions.value = true
    const { data } = await getRegions(props.modelValue.country || "", props.modelValue.federalDistrict || undefined)
    regions.value = data.value ?? []
    loadingRegions.value = false
  }
  if (!cities.value.length) {
    loadingCities.value = true
    const { data } = await getCities(props.modelValue.country || "")
    cities.value = data.value ?? []
    loadingCities.value = false
  }
}

const handleCountryChange = async (country: LocationItem) => {
  emit('update:modelValue', {
    ...props.modelValue,
    country: country.value,
    federalDistrict: '',
    region: '',
    city: ''
  })
  await loadLocations()
  emit('search', props.modelValue)
}

const handleFederalDistrictChange = async (district: LocationItem) => {
  emit('update:modelValue', {
    ...props.modelValue,
    federalDistrict: district.value,
    region: '',
    city: ''
  })
  await loadLocations()
  emit('search', props.modelValue)
}

const handleRegionChange = async (region: LocationItem) => {
  emit('update:modelValue', {
    ...props.modelValue,
    region: region.value,
    city: ''
  })
  await loadLocations()
  emit('search', props.modelValue)
}

const handleCityChange = (city: LocationItem) => {
  emit('update:modelValue', {
    ...props.modelValue,
    city: city.value
  })
  emit('search', props.modelValue)
}

const handleNameChange = (name: string) => {
  emit('update:modelValue', {
    ...props.modelValue,
    name
  })
  emit('search', props.modelValue)
}

// Load initial data
loadLocations()
</script>

<template>
  <section class="bg-white rounded-lg p-6 shadow-sm">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <UFormField label="Название">
        <UInput
            v-model="modelValue.name"
            placeholder="Поиск по названию"
            @update:model-value="handleNameChange"
        />
      </UFormField>

      <UFormField label="Страна">
        <USelectMenu
            :model-value="modelValue.country"
            :items="countries"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите страну"
            searchable
            :loading="loadingCountries"
            @update:model-value="(val) => handleCountryChange(val as LocationItem)"
        />
      </UFormField>

      <UFormField
          v-if="showFederalDistricts"
          label="Федеральный округ"
      >
        <USelectMenu
            :model-value="modelValue.federalDistrict"
            :items="federalDistricts"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите федеральный округ"
            searchable
            :loading="loadingFederalDistricts"
            @update:model-value="(val) => handleFederalDistrictChange(val as LocationItem)"
        />
      </UFormField>

      <UFormField label="Регион">
        <USelectMenu
            :model-value="modelValue.region"
            :items="regions"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите регион"
            searchable
            :loading="loadingRegions"
            @update:model-value="(val) => handleRegionChange(val as LocationItem)"
        />
      </UFormField>

      <UFormField label="Город">
        <USelectMenu
            :model-value="modelValue.city"
            :items="cities"
            :search-input="{
              placeholder: 'Поиск',
              icon: 'i-lucide-search'
            }"
            placeholder="Выберите город"
            searchable
            :disabled="!modelValue.country"
            :loading="loadingCities"
            @update:model-value="(val) => handleCityChange(val as LocationItem)"
        />
      </UFormField>
    </div>
  </section>
</template> 
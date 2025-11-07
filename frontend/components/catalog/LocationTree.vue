<template>
  <div class="location-tree-container">
    <!-- Заголовок -->
    <div class="tree-header">
      <h3 class="tree-title">Выберите нужные города:</h3>
      <div v-if="selectedCount === 0" class="attention-message">
        <Icon name="heroicons:exclamation-triangle" class="attention-icon" />
        <span class="attention-text">Города не выбраны. Настройте свою выборку.</span>
      </div>
    </div>

    <!-- Поиск -->
    <div class="search-container">
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск города/региона"
          class="search-input"
        />
        <Icon name="lucide:search" class="search-icon" />
      </div>
    </div>

    <!-- Дерево локаций -->
    <div class="geo-tree">
      <ul class="tree-ul tree-ul-root">
        <li
          v-for="country in filteredCountries"
          :key="country.value"
          class="tree-item"
        >
          <!-- Страна -->
          <div class="node-view-line flag">
            <img
              :src="getCountryFlag(country.value)"
              :alt="country.label"
              class="node-view-line__img"
            />
            <span
              class="node-view-line-expander"
              :class="{ expanded: expandedCountries.has(country.value) }"
              @click="toggleCountry(country.value)"
            >
              <Icon name="lucide:chevron-down" />
            </span>
            <div class="tree-ul-line">
              <div class="checkbox-button-label">
                <div class="container">
                  <div class="tick" :class="{ checked: isCountrySelected(country.value) }">
                    <Icon v-if="isCountrySelected(country.value)" name="lucide:check" />
                  </div>
                </div>
                <div class="text">{{ country.label }}</div>
              </div>
            </div>
          </div>

          <!-- Регионы (раскрывающийся список) -->
          <ul
            v-if="expandedCountries.has(country.value)"
            class="tree-ul"
          >
            <li
              v-for="region in getRegionsForCountry(country.value)"
              :key="region.value"
              class="tree-item"
            >
              <!-- Регион -->
              <div class="node-view-line">
                <span
                  class="node-view-line-expander"
                  :class="{ expanded: expandedRegions.has(region.value) }"
                  @click="toggleRegion(region.value)"
                >
                  <Icon name="lucide:chevron-down" />
                </span>
                <div class="tree-ul-line">
                  <div class="checkbox-button-label">
                    <div class="container">
                      <div class="tick" :class="{ checked: isRegionSelected(region.value) }">
                        <Icon v-if="isRegionSelected(region.value)" name="lucide:check" />
                      </div>
                    </div>
                    <div class="text">{{ region.label }}</div>
                  </div>
                </div>
              </div>

              <!-- Города (раскрывающийся список) -->
              <ul
                v-if="expandedRegions.has(region.value)"
                class="tree-ul"
              >
                <li
                  v-for="city in getCitiesForRegion(country.value, region.value)"
                  :key="city.value"
                  class="tree-item"
                >
                  <div class="node-view-line">
                    <div class="tree-ul-line">
                      <div class="checkbox-button-label">
                        <div class="container">
                          <div class="tick" :class="{ checked: isCitySelected(city.value) }">
                            <Icon v-if="isCitySelected(city.value)" name="lucide:check" />
                          </div>
                        </div>
                        <div class="text">{{ city.label }}</div>
                      </div>
                    </div>
                  </div>
                </li>
              </ul>
            </li>
          </ul>
        </li>
      </ul>
    </div>

    <!-- Счетчик выбранных -->
    <div class="selection-counter">
      <span>Выбрано: {{ selectedCount }} городов</span>
    </div>

    <!-- Кнопки действий -->
    <div class="action-buttons">
      <button
        class="btn-primary"
        :disabled="selectedCount === 0"
        @click="applySelection"
      >
        Выбрать
      </button>
      <button class="btn-secondary" @click="clearSelection">
        Сброс
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

// Props
interface Props {
  modelValue?: string[]
  countries?: Array<{ label: string; value: string }>
  regions?: Array<{ label: string; value: string }>
  cities?: Array<{ label: string; value: string }>
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  countries: () => [],
  regions: () => [],
  cities: () => []
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'selection-change': [selection: { countries: string[]; regions: string[]; cities: string[] }]
}>()

// Reactive data
const searchQuery = ref('')
const expandedCountries = ref(new Set<string>())
const expandedRegions = ref(new Set<string>())
const selectedCities = ref(new Set<string>())
const selectedRegions = ref(new Set<string>())
const selectedCountries = ref(new Set<string>())

// Computed
const filteredCountries = computed(() => {
  if (!searchQuery.value) return props.countries
  
  return props.countries.filter(country =>
    country.label.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectedCount = computed(() => {
  return selectedCities.value.size
})

// Methods
const getCountryFlag = (countryCode: string) => {
  const flags: Record<string, string> = {
    'RU': '/images/country1.png',
    'KZ': '/images/country3.png', 
    'BY': '/images/country4.png',
    'UA': '/images/country2.png'
  }
  return flags[countryCode] || '/images/country1.png'
}

const toggleCountry = (countryCode: string) => {
  if (expandedCountries.value.has(countryCode)) {
    expandedCountries.value.delete(countryCode)
  } else {
    expandedCountries.value.add(countryCode)
    // Загружаем регионы для страны
    loadRegionsForCountry(countryCode)
  }
}

const toggleRegion = (regionCode: string) => {
  if (expandedRegions.value.has(regionCode)) {
    expandedRegions.value.delete(regionCode)
  } else {
    expandedRegions.value.add(regionCode)
    // Загружаем города для региона
    const countryCode = getCountryForRegion(regionCode)
    if (countryCode) {
      loadCitiesForRegion(countryCode, regionCode)
    }
  }
}

const getRegionsForCountry = (countryCode: string) => {
  return props.regions.filter(region => 
    region.value.startsWith(countryCode)
  )
}

const getCitiesForRegion = (countryCode: string, regionCode: string) => {
  return props.cities.filter(city =>
    city.value.startsWith(`${countryCode}_${regionCode}`)
  )
}

const getCountryForRegion = (regionCode: string) => {
  const region = props.regions.find(r => r.value === regionCode)
  return region ? region.value.split('_')[0] : null
}

const isCountrySelected = (countryCode: string) => {
  return selectedCountries.value.has(countryCode)
}

const isRegionSelected = (regionCode: string) => {
  return selectedRegions.value.has(regionCode)
}

const isCitySelected = (cityCode: string) => {
  return selectedCities.value.has(cityCode)
}

const loadRegionsForCountry = async (countryCode: string) => {
  // Здесь будет загрузка регионов через API
  console.log('Loading regions for country:', countryCode)
}

const loadCitiesForRegion = async (countryCode: string, regionCode: string) => {
  // Здесь будет загрузка городов через API
  console.log('Loading cities for region:', countryCode, regionCode)
}

const applySelection = () => {
  const selection = {
    countries: Array.from(selectedCountries.value),
    regions: Array.from(selectedRegions.value),
    cities: Array.from(selectedCities.value)
  }
  emit('selection-change', selection)
  emit('update:modelValue', Array.from(selectedCities.value))
}

const clearSelection = () => {
  selectedCities.value.clear()
  selectedRegions.value.clear()
  selectedCountries.value.clear()
  applySelection()
}

// Lifecycle
onMounted(() => {
  // Инициализация
})
</script>

<style scoped>
.location-tree-container {
  @apply bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto;
}

.tree-header {
  @apply mb-4;
}

.tree-title {
  @apply text-lg font-semibold text-gray-800 mb-2;
}

.attention-message {
  @apply flex items-center gap-2 text-amber-600 bg-amber-50 p-3 rounded-md;
}

.attention-icon {
  @apply w-6 h-6;
}

.attention-text {
  @apply text-sm;
}

.search-container {
  @apply mb-4;
}

.search-bar {
  @apply relative;
}

.search-input {
  @apply w-full px-4 py-2 pr-10 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent;
}

.search-icon {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400;
}

.geo-tree {
  @apply max-h-96 overflow-y-auto border border-gray-200 rounded-md;
}

.tree-ul {
  @apply list-none p-0 m-0;
}

.tree-ul-root {
  @apply p-2;
}

.tree-item {
  @apply mb-1;
}

.node-view-line {
  @apply flex items-center gap-2 py-1 px-2 hover:bg-gray-50 rounded;
}

.node-view-line.flag {
  @apply font-medium;
}

.node-view-line__img {
  @apply w-6 h-4 object-cover rounded;
}

.node-view-line-expander {
  @apply cursor-pointer p-1 hover:bg-gray-200 rounded transition-transform duration-200;
}

.node-view-line-expander.expanded {
  @apply transform rotate-180;
}

.tree-ul-line {
  @apply flex items-center gap-2 flex-1;
}

.checkbox-button-label {
  @apply flex items-center gap-2 cursor-pointer;
}

.container {
  @apply relative;
}

.tick {
  @apply w-4 h-4 border-2 border-gray-300 rounded flex items-center justify-center transition-colors duration-200;
}

.tick.checked {
  @apply bg-blue-500 border-blue-500 text-white;
}

.text {
  @apply text-sm text-gray-700;
}

.selection-counter {
  @apply text-sm text-gray-600 mt-4 p-2 bg-gray-50 rounded;
}

.action-buttons {
  @apply flex gap-3 mt-4;
}

.btn-primary {
  @apply px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors duration-200;
}
</style>

<template>
  <div class="cities-filter">
    <div class="filter-header">
      <h3 class="filter-title">География выборки:</h3>
      <div class="selected-count" v-if="selectedCitiesCount > 0">
        Выбрано городов: {{ selectedCitiesCount }}
      </div>
    </div>

    <div class="filter-content">
      <!-- Поиск -->
      <div class="search-section">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Поиск по городам..."
          class="search-input"
          @input="onSearchInput"
        />
      </div>

      <!-- Фильтры -->
      <div class="filters-section">
        <label class="filter-checkbox">
          <input
            v-model="filters.millionCitiesOnly"
            type="checkbox"
            @change="onFilterChange"
          />
          Только города-миллионники
        </label>
        <label class="filter-checkbox">
          <input
            v-model="filters.regionalCentersOnly"
            type="checkbox"
            @change="onFilterChange"
          />
          Только региональные центры
        </label>
      </div>

      <!-- Дерево локаций -->
      <div class="location-tree" v-if="!isLoading">
        <div
          v-for="country in locationTree.countries"
          :key="country.id"
          class="country-section"
        >
          <div class="country-header" @click="toggleCountry(country.id)">
            <span class="country-name">{{ country.name }}</span>
            <span class="toggle-icon" :class="{ expanded: expandedCountries.has(country.id) }">
              ▼
            </span>
          </div>

          <div
            v-if="expandedCountries.has(country.id)"
            class="federal-districts"
          >
            <div
              v-for="district in country.federal_districts"
              :key="district.id"
              class="district-section"
            >
              <div class="district-header" @click="toggleDistrict(district.id)">
                <span class="district-name">{{ district.name }}</span>
                <span class="toggle-icon" :class="{ expanded: expandedDistricts.has(district.id) }">
                  ▼
                </span>
              </div>

              <div
                v-if="expandedDistricts.has(district.id)"
                class="regions"
              >
                <div
                  v-for="region in district.regions"
                  :key="region.id"
                  class="region-section"
                >
                  <div class="region-header" @click="toggleRegion(region.id)">
                    <span class="region-name">{{ region.name }}</span>
                    <span class="toggle-icon" :class="{ expanded: expandedRegions.has(region.id) }">
                      ▼
                    </span>
                  </div>

                  <div
                    v-if="expandedRegions.has(region.id)"
                    class="cities"
                  >
                    <div
                      v-for="city in region.cities"
                      :key="city.id"
                      class="city-item"
                    >
                      <label class="city-checkbox">
                        <input
                          :value="city.name"
                          v-model="selectedCities"
                          type="checkbox"
                          @change="onCitySelectionChange"
                        />
                        <span class="city-name">{{ city.name }}</span>
                        <span class="city-population" v-if="city.population">
                          ({{ formatPopulation(city.population) }})
                        </span>
                        <span class="city-badges">
                          <span v-if="city.is_million_city" class="badge million">М</span>
                          <span v-if="city.is_regional_center" class="badge regional">РЦ</span>
                        </span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Загрузка -->
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
        <span>Загрузка данных...</span>
      </div>

      <!-- Ошибка -->
      <div v-if="error" class="error">
        <span>Ошибка загрузки данных: {{ error }}</span>
        <button @click="loadData" class="retry-btn">Повторить</button>
      </div>

      <!-- Статистика -->
      <div v-if="stats" class="stats">
        <div class="stat-item">
          <span class="stat-label">Всего городов:</span>
          <span class="stat-value">{{ stats.total_cities }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Города-миллионники:</span>
          <span class="stat-value">{{ stats.million_cities }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Региональные центры:</span>
          <span class="stat-value">{{ stats.regional_centers }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'

// Типы данных
interface City {
  id: number
  name: string
  population?: number
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
}

interface LocationTree {
  countries: Country[]
  total_countries: number
  total_federal_districts: number
  total_regions: number
  total_cities: number
}

interface Stats {
  total_cities: number
  million_cities: number
  regional_centers: number
  total_federal_districts: number
  total_regions: number
}

// Реактивные данные
const isLoading = ref(false)
const error = ref<string | null>(null)
const locationTree = ref<LocationTree>({ countries: [], total_countries: 0, total_federal_districts: 0, total_regions: 0, total_cities: 0 })
const stats = ref<Stats | null>(null)
const searchQuery = ref('')
const selectedCities = ref<string[]>([])

// Состояние развернутых секций
const expandedCountries = ref(new Set<number>())
const expandedDistricts = ref(new Set<number>())
const expandedRegions = ref(new Set<number>())

// Фильтры
const filters = reactive({
  millionCitiesOnly: false,
  regionalCentersOnly: false
})

// Вычисляемые свойства
const selectedCitiesCount = computed(() => selectedCities.value.length)

// Методы
const loadData = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const { $api } = useNuxtApp()
    
    // Загружаем дерево локаций
    const treeResponse = await $api.get('/v1/cities-filter/cities-filter')
    locationTree.value = treeResponse
    
    // Загружаем статистику
    const statsResponse = await $api.get('/v1/cities-filter/cities-stats')
    stats.value = statsResponse
    
    // Разворачиваем первую страну по умолчанию
    if (locationTree.value.countries.length > 0) {
      expandedCountries.value.add(locationTree.value.countries[0].id)
    }
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Неизвестная ошибка'
    console.error('Ошибка загрузки данных:', err)
  } finally {
    isLoading.value = false
  }
}

const onSearchInput = debounce(() => {
  // Здесь можно добавить логику поиска
  console.log('Поиск:', searchQuery.value)
}, 300)

const onFilterChange = () => {
  // Здесь можно добавить логику фильтрации
  console.log('Фильтры изменились:', filters)
}

const onCitySelectionChange = () => {
  // Эмитим событие изменения выбранных городов
  emit('cities-changed', selectedCities.value)
}

const toggleCountry = (countryId: number) => {
  if (expandedCountries.value.has(countryId)) {
    expandedCountries.value.delete(countryId)
  } else {
    expandedCountries.value.add(countryId)
  }
}

const toggleDistrict = (districtId: number) => {
  if (expandedDistricts.value.has(districtId)) {
    expandedDistricts.value.delete(districtId)
  } else {
    expandedDistricts.value.add(districtId)
  }
}

const toggleRegion = (regionId: number) => {
  if (expandedRegions.value.has(regionId)) {
    expandedRegions.value.delete(regionId)
  } else {
    expandedRegions.value.add(regionId)
  }
}

const formatPopulation = (population: number): string => {
  if (population >= 1000000) {
    return `${(population / 1000000).toFixed(1)}М`
  } else if (population >= 1000) {
    return `${(population / 1000).toFixed(0)}К`
  }
  return population.toString()
}

// Утилита для debounce
function debounce(func: Function, wait: number) {
  let timeout: NodeJS.Timeout
  return function executedFunction(...args: any[]) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Эмиты
const emit = defineEmits<{
  'cities-changed': [cities: string[]]
}>()

// Хуки
onMounted(() => {
  loadData()
})

// Следим за изменениями выбранных городов
watch(selectedCities, (newCities) => {
  emit('cities-changed', newCities)
}, { deep: true })
</script>

<style scoped>
.cities-filter {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

.filter-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.selected-count {
  background: #f0f8ff;
  color: #0066cc;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
}

.search-section {
  margin-bottom: 15px;
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #0066cc;
}

.filters-section {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
}

.filter-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
}

.filter-checkbox input[type="checkbox"] {
  margin: 0;
}

.location-tree {
  max-height: 400px;
  overflow-y: auto;
}

.country-section,
.district-section,
.region-section {
  margin-bottom: 8px;
}

.country-header,
.district-header,
.region-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.country-header:hover,
.district-header:hover,
.region-header:hover {
  background: #e9ecef;
}

.country-name,
.district-name,
.region-name {
  font-weight: 500;
  color: #333;
}

.toggle-icon {
  transition: transform 0.2s;
  color: #666;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

.federal-districts,
.regions,
.cities {
  margin-left: 20px;
  margin-top: 8px;
}

.city-item {
  margin-bottom: 4px;
}

.city-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.city-checkbox:hover {
  background: #f8f9fa;
}

.city-checkbox input[type="checkbox"] {
  margin: 0;
}

.city-name {
  font-weight: 500;
  color: #333;
}

.city-population {
  color: #666;
  font-size: 12px;
}

.city-badges {
  display: flex;
  gap: 4px;
}

.badge {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.million {
  background: #ff6b6b;
  color: white;
}

.badge.regional {
  background: #4ecdc4;
  color: white;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px;
  color: #666;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e0e0e0;
  border-top: 2px solid #0066cc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background: #ffe6e6;
  color: #cc0000;
  border-radius: 4px;
  margin-bottom: 15px;
}

.retry-btn {
  background: #cc0000;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.retry-btn:hover {
  background: #aa0000;
}

.stats {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}
</style>

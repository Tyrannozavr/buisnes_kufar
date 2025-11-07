<template>
  <div class="cities-filter-demo">
    <div class="demo-header">
      <h1>Фильтр городов России</h1>
      <p>Демонстрация фильтра городов как на сайте export-base.ru</p>
    </div>

    <div class="demo-content">
      <div class="filter-section">
        <CitiesFilter @cities-changed="onCitiesChanged" />
      </div>

      <div class="results-section">
        <h3>Выбранные города:</h3>
        <div v-if="selectedCities.length === 0" class="no-selection">
          Города не выбраны
        </div>
        <div v-else class="selected-cities">
          <div
            v-for="city in selectedCities"
            :key="city"
            class="selected-city"
          >
            {{ city }}
            <button @click="removeCity(city)" class="remove-btn">×</button>
          </div>
        </div>
      </div>

      <div class="actions-section">
        <button @click="selectAllMillionCities" class="action-btn">
          Выбрать все города-миллионники
        </button>
        <button @click="selectAllRegionalCenters" class="action-btn">
          Выбрать все региональные центры
        </button>
        <button @click="clearSelection" class="action-btn clear">
          Очистить выбор
        </button>
      </div>

      <div class="info-section">
        <h3>Информация о фильтре:</h3>
        <ul>
          <li>Фильтр показывает все города России, разбитые по федеральным округам и регионам</li>
          <li>Можно искать города по названию</li>
          <li>Доступны фильтры по типу города (миллионники, региональные центры)</li>
          <li>Показывается население и специальные метки для городов</li>
          <li>Можно выбирать города индивидуально или группами</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CitiesFilter from '~/components/CitiesFilter.vue'

// Реактивные данные
const selectedCities = ref<string[]>([])

// Методы
const onCitiesChanged = (cities: string[]) => {
  selectedCities.value = cities
}

const removeCity = (city: string) => {
  const index = selectedCities.value.indexOf(city)
  if (index > -1) {
    selectedCities.value.splice(index, 1)
  }
}

const selectAllMillionCities = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/v1/cities-filter/cities-search', {
      params: {
        query: '',
        million_cities_only: true
      }
    })
    
    const millionCities = response.items.map((item: any) => item.label)
    selectedCities.value = [...new Set([...selectedCities.value, ...millionCities])]
  } catch (error) {
    console.error('Ошибка загрузки городов-миллионников:', error)
  }
}

const selectAllRegionalCenters = async () => {
  try {
    const { $api } = useNuxtApp()
    const response = await $api.get('/v1/cities-filter/cities-search', {
      params: {
        query: '',
        regional_centers_only: true
      }
    })
    
    const regionalCenters = response.items.map((item: any) => item.label)
    selectedCities.value = [...new Set([...selectedCities.value, ...regionalCenters])]
  } catch (error) {
    console.error('Ошибка загрузки региональных центров:', error)
  }
}

const clearSelection = () => {
  selectedCities.value = []
}

// Мета-данные страницы
useHead({
  title: 'Фильтр городов - Демо',
  meta: [
    { name: 'description', content: 'Демонстрация фильтра городов России' }
  ]
})
</script>

<style scoped>
.cities-filter-demo {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.demo-header {
  text-align: center;
  margin-bottom: 40px;
}

.demo-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.demo-header p {
  color: #666;
  font-size: 16px;
}

.demo-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.filter-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}

.results-section {
  background: white;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.results-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.no-selection {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 20px;
}

.selected-cities {
  max-height: 300px;
  overflow-y: auto;
}

.selected-city {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: #e3f2fd;
  border-radius: 4px;
  color: #1976d2;
}

.remove-btn {
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background: #d32f2f;
}

.actions-section {
  grid-column: 1 / -1;
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 20px;
}

.action-btn {
  background: #0066cc;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background: #0052a3;
}

.action-btn.clear {
  background: #666;
}

.action-btn.clear:hover {
  background: #555;
}

.info-section {
  grid-column: 1 / -1;
  background: #f0f8ff;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.info-section h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.info-section ul {
  margin: 0;
  padding-left: 20px;
}

.info-section li {
  margin-bottom: 8px;
  color: #555;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .demo-content {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
    align-items: center;
  }
  
  .action-btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>

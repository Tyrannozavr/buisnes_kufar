<template>
  <div class="space-y-8">
    <!-- Search and Filters -->
    <section class="bg-white rounded-lg p-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UFormGroup label="Название">
          <UInput
            v-model="search.name"
            placeholder="Поиск по названию"
          />
        </UFormGroup>

        <UFormGroup label="Страна">
          <USelect
            v-model="search.country"
            :options="countries"
            placeholder="Выберите страну"
          />
        </UFormGroup>

        <UFormGroup label="Федеральный округ">
          <USelect
            v-model="search.region"
            :options="regions"
            placeholder="Выберите округ"
            :disabled="!search.country || search.country !== 'Россия'"
          />
        </UFormGroup>

        <UFormGroup label="Регион">
          <USelect
            v-model="search.city"
            :options="cities"
            placeholder="Выберите регион"
          />
        </UFormGroup>
      </div>
    </section>

    <!-- Products Grid -->
    <section>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-6">
        <ProductCard
          v-for="product in filteredProducts"
          :key="product.id"
          :product="product"
          @add-to-cart="handleAddToCart"
        />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { Product } from '~/types'
import { mockProducts, mockCompanies } from '~/utils/mockData'

// Mock data for filters
const countries = [
  'Россия',
  'Азербайджан',
  'Армения',
  'Беларусь',
  'Казахстан',
  'Кыргызстан',
  'Молдова',
  'Таджикистан',
  'Узбекистан'
]

const regions = [
  'Центральный',
  'Северо-Западный',
  'Южный',
  'Северо-Кавказский',
  'Приволжский',
  'Уральский',
  'Сибирский',
  'Дальневосточный'
]

const cities = [
  'Москва',
  'Санкт-Петербург',
  'Новосибирск',
  'Екатеринбург',
  'Казань'
]

// Search state
const search = ref({
  name: '',
  country: '',
  region: '',
  city: ''
})

// Filtered products
const filteredProducts = computed(() => {
  return mockProducts.filter(product => {
    const company = mockCompanies.find(c => c.id === product.companyId)
    if (!company) return false

    const matchesName = !search.value.name || 
      product.name.toLowerCase().includes(search.value.name.toLowerCase())
    
    const matchesCountry = !search.value.country || 
      company.country === search.value.country
    
    const matchesRegion = !search.value.region || 
      company.region === search.value.region
    
    const matchesCity = !search.value.city || 
      company.city === search.value.city

    return matchesName && matchesCountry && matchesRegion && matchesCity
  })
})

// Handle add to cart
const handleAddToCart = (product: Product) => {
  // TODO: Implement cart functionality
  console.log('Added to cart:', product)
}
</script> 
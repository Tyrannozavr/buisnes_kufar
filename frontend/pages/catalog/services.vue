<script setup lang="ts">
import ProductCard from "~/components/catalog/ProductCard.vue";
import { useProductsApi } from '~/api/products'
import ProductsFilter from "~/components/catalog/ProductsFilter.vue";

// API
const { searchServices } = useProductsApi()

// Search state
const search = ref({
  name: '',
  country: '',
  federalDistrict: '',
  region: '',
  city: ''
})

// Loading and error states
const loading = ref(false)
const error = ref<string | null>(null)

// Load products with SSR support
const { data: products } = await useAsyncData(
    'products',
    async () => {
      try {
        const { data } = await searchServices(search.value)
        return data.value ?? []
      } catch (e) {
        error.value = 'Failed to load products'
        console.error(e)
        return []
      }
    }
)

// Handle search updates
const handleSearch = async (newSearch: typeof search.value) => {
  search.value = newSearch
  loading.value = true
  try {
    const { data } = await searchServices(newSearch)
    products.value = data.value ?? []
  } catch (e) {
    error.value = 'Failed to load products'
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Каталог услуг</h1>

    <!-- Filters -->
    <ProductsFilter
        v-model="search"
        @search="handleSearch"
        class="mb-8"
    />

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-8">
      <UIcon name="i-heroicons-arrow-path" class="animate-spin text-4xl" />
    </div>

    <!-- Error State -->
    <UAlert
        v-else-if="error"
        :title="error"
        color="error"
        class="mb-8"
    />

    <!-- Products Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      <ProductCard
          v-for="product in (products ?? [])"
          :key="product.id"
          :product="product"
      />
    </div>

    <!-- Empty State -->
    <div
        v-if="!loading && !error && (!products || products.length === 0)"
        class="text-center py-8 text-gray-500"
    >
      Не найдено продуктов подходящих к вашему запросу.
    </div>
  </div>
</template>
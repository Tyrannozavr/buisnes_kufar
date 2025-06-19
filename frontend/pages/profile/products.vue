<script setup lang="ts">
import CompanyProducts from "~/components/company/CompanyProducts.vue"
import { getMyProducts } from '~/api/me/products'
import type { ProductResponse } from '~/types/product'

definePageMeta({
  layout: 'profile'
})

// State
const products = ref<ProductResponse[]>([])
const loading = ref(false)

// Fetch company products
const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await getMyProducts({
      include_hidden: true,
      include_deleted: true
    })
    products.value = response.products
  } catch (error) {
    console.error('Error fetching products:', error)
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось загрузить продукты',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

// Handle refresh event from CompanyProducts component
const handleRefresh = () => {
  fetchProducts()
}

// Initial fetch
await fetchProducts()
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Продукция</h2>
      <div v-if="loading" class="flex justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-400" />
      </div>
      <CompanyProducts 
        v-else
        mode="owner" 
        :products="products" 
        @refresh="handleRefresh"
      />
    </div>
  </div>
</template>
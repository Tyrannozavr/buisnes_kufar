<script setup lang="ts">
import ProductCard from "~/components/catalog/ProductCard.vue";
import CatalogFilter from "~/components/catalog/CatalogFilter.vue";
import { useProductsApi } from '~/api/products'
import type { ProductSearchParams, ServiceSearchParams } from '~/types/filters'

const props = defineProps<{
  type: 'products' | 'services'
  title: string
}>()

// API
const { searchProducts, searchServices } = useProductsApi()
const currentPage = ref(1)

// Search state
const search = ref<ProductSearchParams | ServiceSearchParams>({
  search: '',
  country: '',
  federalDistrict: '',
  region: '',
  city: '',
  type: '',
  minPrice: undefined,
  maxPrice: undefined,
  inStock: undefined
})

// Loading and error states
const loading = ref(false)
const error = ref<string | null>(null)

// Load items
const { data: items, pending: isPending } = await (props.type === 'products' ? searchProducts : searchServices)(search.value)

// Handle search updates
const handleSearch = async (newSearch: ProductSearchParams | ServiceSearchParams) => {
  search.value = newSearch
  loading.value = true
  try {
    const { data } = await (props.type === 'products' ? searchProducts : searchServices)(newSearch)
    if (data.value) {
      items.value = data.value
    }
  } catch (e) {
    error.value = `Failed to load ${props.type}`
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <UContainer>
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold">{{ title }}</h1>
      </div>

      <!-- Filter -->
      <CatalogFilter
        :type="type"
        :title="title"
        @search="handleSearch"
      />

      <div v-if="isPending" class="flex justify-center items-center h-64">
        <ULoadingIcon />
      </div>

      <div v-else-if="error" class="text-red-500 text-center">
        {{ error }}
      </div>

      <div v-else>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <ProductCard
            v-for="item in items?.data"
            :key="item.id"
            :product="item"
          />
        </div>

        <div v-if="items?.pagination" class="mt-6 flex justify-center">
          <UPagination
            v-model="currentPage"
            :total="items.pagination.total"
            :page-count="items.pagination.totalPages"
            :per-page="items.pagination.perPage"
          />
        </div>
      </div>
    </UContainer>
  </div>
</template> 
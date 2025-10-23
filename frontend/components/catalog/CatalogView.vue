<script setup lang="ts">
import ProductCard from "~/components/catalog/ProductCard.vue";
import CatalogFilter from "~/components/catalog/CatalogFilter.vue";
import { useProductsApi } from '~/api/products'
import { useProductFilters, useServiceFilters } from '~/api/filters'
import type { ProductItemPublic, ProductListPublicResponse } from '~/types/product'
import type { ProductFilterRequest, ServiceFilterRequest } from '~/api/filters'

const props = defineProps<{
  type: 'products' | 'services'
  title: string
}>()

// API
const { getAllGoods, getAllServices } = useProductsApi()
const { searchProducts } = useProductFilters()
const { searchServices } = useServiceFilters()
const currentPage = ref(1)

// Loading and error states
const loading = ref(false)
const error = ref<string | null>(null)

// Convert ProductResponse to ProductItemPublic
const convertToProductItemPublic = (product: any): ProductItemPublic => {
  return {
    name: product.name,
    logo_url: product.images?.[0] || null,
    slug: product.slug,
    description: product.description || '',
    article: product.article,
    type: product.type,
    price: product.price,
    unit_of_measurement: product.unit_of_measurement || 'шт'
  }
}

// Load items based on type
const { data: items, pending: isPending, refresh } = await useAsyncData<ProductListPublicResponse>(
  `catalog-${props.type}`,
  async () => {
    if (props.type === 'products') {
      const result = await getAllGoods({ skip: 0, limit: 20 })
      return {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    } else {
      const result = await getAllServices({ skip: 0, limit: 20 })
      return {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    }
  }
)

// Handle search with filters
const handleSearch = async (searchParams: any) => {
  loading.value = true
  error.value = null
  
  try {
    // Convert frontend params to API format
    const apiParams = {
      search: searchParams.search || undefined,
      country: searchParams.country || undefined,
      federal_district: searchParams.federalDistrict || undefined,
      region: searchParams.region || undefined,
      city: searchParams.city || undefined,
      min_price: searchParams.minPrice || undefined,
      max_price: searchParams.maxPrice || undefined,
      in_stock: searchParams.inStock || undefined,
      skip: 0,
      limit: 20
    }
    
    let result
    if (props.type === 'products') {
      result = await searchProducts(apiParams)
    } else {
      result = await searchServices(apiParams)
    }
    
    items.value = {
      products: result.products.map(convertToProductItemPublic),
      total: result.total,
      page: result.page,
      per_page: result.per_page
    }
    
    currentPage.value = 1
  } catch (e) {
    error.value = `Ошибка поиска ${props.type === 'products' ? 'товаров' : 'услуг'}`
    console.error(e)
  } finally {
    loading.value = false
  }
}

// Handle pagination
const handlePageChange = async (page: number) => {
  currentPage.value = page
  const skip = (page - 1) * 20
  
  try {
    if (props.type === 'products') {
      const result = await getAllGoods({ skip, limit: 20 })
      items.value = {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    } else {
      const result = await getAllServices({ skip, limit: 20 })
      items.value = {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    }
  } catch (e) {
    error.value = `Failed to load ${props.type}`
    console.error(e)
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

      <div v-if="isPending || loading" class="flex justify-center items-center h-64">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" />
      </div>

      <div v-else-if="error" class="text-red-500 text-center">
        {{ error }}
      </div>

      <div v-else>
        <div v-if="!items?.products || items.products.length === 0" class="text-center text-gray-500 py-8">
          {{ type === 'products' ? 'Товары не найдены' : 'Услуги не найдены' }}
        </div>
        
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <ProductCard
            v-for="item in items.products"
            :key="item.slug"
            :product="item"
          />
        </div>

        <div v-if="items?.total && items.total > 20" class="mt-6 flex justify-center">
          <UPagination
            v-model="currentPage"
            :total="items.total"
            :per-page="20"
            @update:model-value="handlePageChange"
          />
        </div>
      </div>
    </UContainer>
  </div>
</template> 
<script setup lang="ts">
import ProductCard from "~/components/catalog/ProductCard.vue";
import CatalogFilter from "~/components/catalog/CatalogFilter.vue";
import CustomPagination from "~/components/ui/CustomPagination.vue";
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

// URL and pagination
const route = useRoute()
const router = useRouter()

// Initialize page from URL
const pageParam = route.query.page
const initialPage = pageParam && typeof pageParam === 'string' ? parseInt(pageParam) : 1
const currentPage = ref(initialPage > 0 ? initialPage : 1)

// Initialize filters from URL
const urlFilters = {
  search: route.query.search as string || undefined,
  cities: route.query.cities ? (route.query.cities as string).split(',') : undefined,
  minPrice: route.query.minPrice ? parseFloat(route.query.minPrice as string) : undefined,
  maxPrice: route.query.maxPrice ? parseFloat(route.query.maxPrice as string) : undefined,
  inStock: route.query.inStock === 'true'
}

onMounted(async () => {
  console.log('🔄 Инициализация страницы из URL:', currentPage.value)

  // If there are URL filters, apply them
  if (urlFilters.search || urlFilters.cities?.length || urlFilters.minPrice || urlFilters.maxPrice || urlFilters.inStock) {
    console.log('🔄 Инициализация фильтров из URL:', urlFilters)
    await handleSearch(urlFilters)
  }
})

// Loading and error states
const loading = ref(false)
const error = ref<string | null>(null)

// Current search filters (for pagination)
const currentFilters = ref<any>(null)

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
    unit_of_measurement: product.unit_of_measurement || 'шт',
		company_id: product.company_id,
		company_name: product.company_name,
  }
}

// Load items based on type
const { data: items, pending: isPending, refresh } = await useAsyncData<ProductListPublicResponse>(
  `catalog-${props.type}`,
  async () => {
    const skip = (currentPage.value - 1) * 20
    if (props.type === 'products') {
      const result = await getAllGoods({ skip, limit: 20 })
      return {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    } else {
      const result = await getAllServices({ skip, limit: 20 })
      return {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    }
  },
  {
    watch: [currentPage]
  }
)

// Handle search with filters
const handleSearch = async (searchParams: any) => {
  loading.value = true
  error.value = null
  
  // Reset to page 1 when searching
  currentPage.value = 1

  try {
    // Convert frontend params to API format
    const apiParams = {
      search: searchParams.search || undefined,
      cities: searchParams.cities || undefined, // Передаем массив выбранных городов
      min_price: searchParams.minPrice || undefined,
      max_price: searchParams.maxPrice || undefined,
      in_stock: searchParams.inStock || undefined,
      skip: 0,
      limit: 20
    }
    
    // Сохраняем текущие фильтры для пагинации
    currentFilters.value = apiParams
    console.log('🔍 Сохранены фильтры для пагинации:', currentFilters.value)

    // Update URL with search params and reset page
    await router.push({
      query: {
        ...route.query,
        page: '1',
        search: searchParams.search || undefined,
        cities: searchParams.cities?.length ? searchParams.cities.join(',') : undefined,
        minPrice: searchParams.minPrice || undefined,
        maxPrice: searchParams.maxPrice || undefined,
        inStock: searchParams.inStock || undefined
      }
    })

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
  console.log('📄 Переключение на страницу:', page)
  console.log('🔍 Текущие фильтры:', currentFilters.value)

  // Update URL
  await router.push({
    query: {
      ...route.query,
      page: page.toString()
    }
  })

  currentPage.value = page
  const skip = (page - 1) * 20
  
  try {
    // Если есть активные фильтры, используем их для пагинации
    if (currentFilters.value) {
      const apiParams = {
        ...currentFilters.value,
        skip,
        limit: 20
      }
      console.log('🚀 Отправляем запрос с фильтрами:', apiParams)

      let result
      if (props.type === 'products') {
        result = await searchProducts(apiParams)
      } else {
        result = await searchServices(apiParams)
      }

      console.log('✅ Получен результат:', result.products.length, 'товаров')
      console.log('📊 Детали результата:', {
        total: result.total,
        page: result.page,
        per_page: result.per_page,
        skip: skip,
        limit: 20,
        calculatedPages: Math.ceil(result.total / 20)
      })

      items.value = {
        products: result.products.map(convertToProductItemPublic),
        total: result.total,
        page: result.page,
        per_page: result.per_page
      }
    } else {
      console.log('⚠️ Нет активных фильтров, используем обычную загрузку')
      console.log('📊 Параметры обычной загрузки:', { skip, limit: 20 })

      // Если нет фильтров, используем обычную загрузку
      if (props.type === 'products') {
        const result = await getAllGoods({ skip, limit: 20 })
        console.log('✅ Результат обычной загрузки:', {
          productsCount: result.products.length,
          total: result.total,
          page: result.page,
          per_page: result.per_page,
          skip: skip
        })

        items.value = {
          products: result.products.map(convertToProductItemPublic),
          total: result.total,
          page: result.page,
          per_page: result.per_page
        }
      } else {
        const result = await getAllServices({ skip, limit: 20 })
        console.log('✅ Результат обычной загрузки услуг:', {
          productsCount: result.products.length,
          total: result.total,
          page: result.page,
          per_page: result.per_page,
          skip: skip
        })

        items.value = {
          products: result.products.map(convertToProductItemPublic),
          total: result.total,
          page: result.page,
          per_page: result.per_page
        }
      }
    }
  } catch (e) {
    error.value = `Failed to load ${props.type}`
    console.error('❌ Ошибка при загрузке страницы:', e)
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
          <CustomPagination
            :current-page="currentPage"
            :total="items.total"
            :per-page="20"
            @update:page="handlePageChange"
          />
        </div>
      </div>
    </UContainer>
  </div>
</template> 
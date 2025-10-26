<script setup lang="ts">
import type {CompanyShort} from '~/types/company'
import {searchServiceProvidersSSR} from "~/api";
import CustomPagination from "~/components/ui/CustomPagination.vue";
import CatalogFilter from "~/components/catalog/CatalogFilter.vue";

const route = useRoute()
const title = 'Поставщики услуг'

// Success message handling
const showSuccessMessage = ref(false)
const successMessage = ref('')

// Pagination state
const pageParam = route.query.page
const initialPage = pageParam && typeof pageParam === 'string' ? parseInt(pageParam) : 1
const currentPage = ref(initialPage > 0 ? initialPage : 1)
const perPage = ref(10)

// Parse filters from URL
const urlFilters = {
  search: route.query.search as string | undefined,
  cities: route.query.cities ? (route.query.cities as string).split(',').map(Number) : undefined,
  minPrice: route.query.minPrice ? parseFloat(route.query.minPrice as string) : undefined,
  maxPrice: route.query.maxPrice ? parseFloat(route.query.maxPrice as string) : undefined,
  inStock: route.query.inStock === 'true'
}

// Fetch service providers with pagination using SSR function
const initialResponse = await searchServiceProvidersSSR(currentPage.value, perPage.value, urlFilters)

// Make response reactive
const response = ref(initialResponse)

// Apply filters from URL if present
if (urlFilters.search || urlFilters.cities?.length || urlFilters.minPrice || urlFilters.maxPrice || urlFilters.inStock) {
  currentFilters.value = urlFilters
}

// Computed properties
const manufacturers = computed(() => response.value?.data || [])
const pagination = computed(() => response.value?.pagination || {
  total: 0,
  page: 1,
  perPage: 10,
  totalPages: 1
})

const manufacturersPending = ref(false)
const manufacturersError = ref<Error | null>(null)

// Store current filters
const currentFilters = ref<any>({})

// Watch for page changes
watch(currentPage, async (newPage) => {
  manufacturersPending.value = true
  try {
    const newResponse = await searchServiceProvidersSSR(newPage, perPage.value, currentFilters.value)
    response.value = newResponse
  } finally {
    manufacturersPending.value = false
  }
})

const router = useRouter()

const handleSearch = async (params: {
  search?: string
  cities?: number[]
  minPrice?: number
  maxPrice?: number
  inStock?: boolean
}) => {
  manufacturersPending.value = true
  manufacturersError.value = null
  currentFilters.value = params
  currentPage.value = 1 // Reset to page 1 when searching

  // Update URL with filters
  await router.push({
    query: {
      ...route.query,
      page: '1',
      search: params.search || undefined,
      cities: params.cities?.length ? params.cities.join(',') : undefined,
      minPrice: params.minPrice || undefined,
      maxPrice: params.maxPrice || undefined,
      inStock: params.inStock || undefined
    }
  })

  try {
    const newResponse = await searchServiceProvidersSSR(currentPage.value, perPage.value, params)
    response.value = newResponse
  } catch (error) {
    console.error('Search error:', error)
    manufacturersError.value = error as Error
  } finally {
    manufacturersPending.value = false
  }
}

// Check if there's a success message in the query parameters
if (route.query.created === 'true') {
  successMessage.value = 'Поставщик услуг успешно добавлен'
  showSuccessMessage.value = true

  // Auto-hide the message after 5 seconds
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 5000)
}

const handlePageChange = async (page: number) => {
  // Update URL with page
  await router.push({
    query: {
      ...route.query,
      page: page.toString()
    }
  })
  currentPage.value = page
}

// Filters are now handled by POST requests
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Success message notification -->
    <div v-if="showSuccessMessage" class="mb-6">
      <UAlert
          variant="solid"
          color="success"
          title="Успешно!"
          :description="successMessage"
          class="mb-4"
          icon="i-heroicons-check-circle"
      >
        <template #footer>
          <div class="flex justify-end">
            <UButton
                color="neutral"
                variant="ghost"
                size="sm"
                @click="showSuccessMessage = false"
            >
              Закрыть
            </UButton>
          </div>
        </template>
      </UAlert>
    </div>

    <h1 class="text-2xl font-bold mb-4">{{ title }}</h1>

    <!-- Search Form -->
    <CatalogFilter type="services" @search="handleSearch"/>
    
    <!-- Loading state -->
    <section v-if="manufacturersPending" class="bg-white rounded-lg p-6 shadow-sm">
      <div class="flex justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>
    </section>

    <!-- Error state -->
    <UAlert v-else-if="manufacturersError" color="error" variant="soft" class="mb-4">
      Не удалось загрузить данные о поставщиках услуг. Пожалуйста, попробуйте позже.
    </UAlert>

    <!-- Empty state -->
    <section v-else-if="manufacturers.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
      <div class="text-center py-8">
        <UIcon name="i-heroicons-building-office" class="h-12 w-12 mx-auto text-gray-400" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">Поставщики услуг не найдены</h3>
        <p class="mt-2 text-sm text-gray-500">
          На данный момент нет доступных поставщиков услуг
        </p>
      </div>
    </section>

    <!-- Service Providers List -->
    <section v-else>
      <CompaniesList
          :manufacturers="manufacturers"
          :pending="manufacturersPending"
          :error="manufacturersError"
      />

      <!-- Pagination -->
      <div class="mt-8 flex justify-center">
        <CustomPagination
          :current-page="currentPage"
          :total="pagination.total"
          :per-page="perPage"
          @update:page="handlePageChange"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Custom styles can be added here */
</style>
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
const currentPage = ref(1)
const perPage = ref(10)

// Fetch service providers with pagination using SSR function
const response = await searchServiceProvidersSSR(currentPage.value, perPage.value)

// Computed properties
const manufacturers = computed(() => response?.data || [])
const pagination = computed(() => response?.pagination || {
  total: 0,
  page: 1,
  perPage: 10,
  totalPages: 1
})

const manufacturersPending = ref(false)
const manufacturersError = ref<Error | null>(null)

// Watch for page changes
watch(currentPage, async (newPage) => {
  // Refresh data when page changes
  const newResponse = await searchServiceProvidersSSR(newPage, perPage.value)
  // Update the response data
  Object.assign(response, newResponse)
})

const handleSearch = async (params: {
  search?: string
  cities?: string[]
  minPrice?: number
  maxPrice?: number
  inStock?: boolean
}) => {
  manufacturersPending.value = true
  manufacturersError.value = null

  try {
    // Преобразуем параметры для API
    const apiParams: any = {}
    if (params.search) apiParams.search = params.search
    if (params.cities && params.cities.length > 0) {
      // Для компаний используем первый выбранный город
      apiParams.city = params.cities[0]
    }
    
    const newResponse = await searchServiceProvidersSSR(currentPage.value, perPage.value, apiParams)
    // Update the response data
    Object.assign(response, newResponse)
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

const handlePageChange = (page: number) => {
  currentPage.value = page
}
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
    <CatalogFilter type="companies" @search="handleSearch"/>
    
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
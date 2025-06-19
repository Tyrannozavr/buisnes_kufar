<script setup lang="ts">
import type {CompanyShort} from '~/types/company'
import {useCompaniesApi} from "~/api";

const route = useRoute()
const title = 'Производители товаров'

// Success message handling
const showSuccessMessage = ref(false)
const successMessage = ref('')

// API
const {searchManufacturers} = useCompaniesApi()

// Manufacturers data
const manufacturers = ref<CompanyShort[]>([])
const manufacturersPending = ref(false)
const manufacturersError = ref<Error | null>(null)

const handleSearch = async (params: {
  search?: string
  country?: string
  federalDistrict?: string
  region?: string
  city?: string
  product?: string
}) => {
  manufacturersPending.value = true
  manufacturersError.value = null

  try {
    const {data} = await searchManufacturers(params)
    manufacturers.value = data.value ?? []
  } catch (error) {
    console.error('Search error:', error)
    manufacturersError.value = error as Error
  } finally {
    manufacturersPending.value = false
  }
}

// Initial data loading during SSR
try {
  // const { data: initialManufacturers } = await searchManufacturers()
  const initialManufacturers = await searchManufacturers()
  manufacturers.value = initialManufacturers ?? []
} catch (error) {
  manufacturersError.value = error as Error
  manufacturers.value = []
}

// Check if there's a success message in the query parameters
if (route.query.created === 'true') {
  successMessage.value = 'Производитель успешно добавлен'
  showSuccessMessage.value = true

  // Auto-hide the message after 5 seconds
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 5000)
}
</script>

<template>
  <div class="container mx-auto">
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
    <CompaniesFilter @search="handleSearch"/>
    <!-- Manufacturers List -->
    <CompaniesList
        :manufacturers="manufacturers"
        :pending="manufacturersPending"
        :error="manufacturersError"
    />
  </div>
</template>

<style scoped>
/* Custom styles can be added here */
</style>
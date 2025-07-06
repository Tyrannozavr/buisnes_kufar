<script setup lang="ts">
import type { Company } from '~/types/company'
import { getCompaniesPaginatedSSR } from '~/api/companies'

// Pagination state
const currentPage = ref(1)
const perPage = ref(10)

// Fetch companies with pagination using SSR function
const response = await getCompaniesPaginatedSSR(currentPage.value, perPage.value)

// Computed properties
const companies = computed(() => response?.data || [])
const pagination = computed(() => response?.pagination || {
  total: 0,
  page: 1,
  perPage: 10,
  totalPages: 1
})

// Watch for page changes
watch(currentPage, async (newPage) => {
  // Refresh data when page changes
  const newResponse = await getCompaniesPaginatedSSR(newPage, perPage.value)
  // Update the response data
  Object.assign(response, newResponse)
})

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Get activity badge color
const getActivityColor = (tradeActivity: string) => {
  switch (tradeActivity) {
    case 'Продавец':
      return 'success'
    case 'Покупатель':
      return 'info'
    case 'Покупатель и продавец':
      return 'primary'
    default:
      return 'neutral'
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Все компании</h1>

      <p class="text-gray-600">Найдите надежных партнеров для вашего бизнеса</p>
    </div>

    <!-- Loading state -->
    <section v-if="false" class="bg-white rounded-lg p-6 shadow-sm">
      <div class="flex justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>
    </section>

    <!-- Error state -->
    <UAlert v-else-if="false" color="error" variant="soft" class="mb-4">
      Не удалось загрузить данные о компаниях. Пожалуйста, попробуйте позже.
    </UAlert>
    <!-- Empty state -->
    <section v-else-if="companies.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
      <div class="text-center py-8">
        <UIcon name="i-heroicons-building-office" class="h-12 w-12 mx-auto text-gray-400" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">Компании не найдены</h3>
        <p class="mt-2 text-sm text-gray-500">
          На данный момент нет доступных компаний
        </p>
      </div>
    </section>

    <!-- Companies List -->
    <section v-else>
      <div class="space-y-4">
        <div 
          v-for="company in companies" 
          :key="company.id" 
          class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div class="p-6">
            <div class="flex items-start gap-6">
              <!-- Company Logo -->
              <div class="flex-shrink-0">
                <NuxtLink :to="`/companies/${company.slug}`" class="block">
                  <NuxtImg
                    :src="company.logo_url || '/images/default-company-logo.png'"
                    :alt="company.name"
                    class="w-20 h-20 object-cover rounded-lg border border-gray-200"
                  />
                </NuxtLink>
              </div>

              <!-- Company Info -->
              <div class="flex-grow min-w-0">
                <div class="flex items-start justify-between">
                  <div class="flex-grow min-w-0">
                    <!-- Company Name and Type -->
                    <div class="flex items-center gap-3 mb-2">
                      <NuxtLink 
                        :to="`/companies/${company.slug}`"
                        class="text-xl font-semibold text-gray-900 hover:text-primary-600 transition-colors"
                      >
                        {{ company.name }}
                      </NuxtLink>
                      <UBadge 
                        :color="getActivityColor(company.tradeActivity)"
                        variant="soft"
                        size="sm"
                      >
                        {{ company.tradeActivity }}
                      </UBadge>
                    </div>

                    <!-- Business Type -->
                    <p class="text-sm text-gray-600 mb-2">
                      {{ company.businessType }}
                    </p>

                    <!-- Description -->
                    <p v-if="company.description" class="text-gray-700 mb-3 line-clamp-2">
                      {{ company.description }}
                    </p>

                    <!-- Location and Registration -->
                    <div class="flex flex-wrap gap-4 text-sm text-gray-500">
                      <div class="flex items-center gap-1">
                        <UIcon name="i-heroicons-map-pin" class="h-4 w-4" />
                        <span>{{ company.city }}, {{ company.region }}</span>
                      </div>
                      <div class="flex items-center gap-1">
                        <UIcon name="i-heroicons-calendar" class="h-4 w-4" />
                        <span>Регистрация: {{ formatDate(company.registrationDate) }}</span>
                      </div>
                      <div v-if="company.phone" class="flex items-center gap-1">
                        <UIcon name="i-heroicons-phone" class="h-4 w-4" />
                        <span>{{ company.phone }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Action Buttons -->
                  <div class="flex flex-col gap-2 ml-4">
                    <UButton
                      :to="`/companies/${company.slug}`"
                      color="primary"
                      variant="soft"
                      size="sm"
                    >
                      Подробнее
                    </UButton>
                    <MessageButton
                      :company-id="company.id"
                      :company-name="company.name"
                      variant="ghost"
                      size="sm"
                      custom-text="Написать"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-8 flex justify-center">
        <UPagination
          v-model="currentPage"
          :total="pagination.total"
          :per-page="perPage"
        />
      </div>
    </section>
  </div>
</template> 
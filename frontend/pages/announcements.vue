<script setup lang="ts">
import type { Announcement } from '~/types/announcement'
import type { Company } from '~/types/company'
import { useApi } from '~/composables/useApi'

// Fetch data using the useApi composable
const currentPage = ref(1)
const perPage = ref(10)

const { data: announcementsData, error: announcementsError, pending: announcementsPending, refresh: refreshAnnouncements } = await useApi<{
  data: Announcement[],
  pagination: {
    total: number,
    page: number,
    perPage: number,
    totalPages: number
  }
}>(`/announcements?page=${currentPage.value}&perPage=${perPage.value}`)

const announcements = computed(() => announcementsData.value?.data || [])
const pagination = computed(() => announcementsData.value?.pagination || {
  total: 0,
  page: 1,
  perPage: 10,
  totalPages: 1
})

// Watch for page changes
watch(currentPage, async (newPage) => {
  await refreshAnnouncements()
})

const { data: companies, error: companiesError, pending: companiesPending } = await useApi<Company[]>('/companies')

// Search state
const search = ref({
  query: '',
  country: ''
})

// Countries for filtering
const countries = computed(() => {
  if (!companies.value) return []
  return [...new Set(companies.value.map(company => company.country))].sort()
})

// Filtered announcements based on search criteria
const filteredAnnouncements = computed(() => {
  if (!announcements.value || !companies.value) return []

  return announcements.value
    .filter(announcement => {
      const company = companies.value?.find(c => c.id === announcement.companyId)
      if (!company) return false

      const matchesQuery = !search.value.query ||
          announcement.title.toLowerCase().includes(search.value.query.toLowerCase()) ||
          announcement.content.toLowerCase().includes(search.value.query.toLowerCase())

      const matchesCountry = !search.value.country ||
          company.country === search.value.country

      return matchesQuery && matchesCountry
    })
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
})

// Helper function to get company name
const getCompanyName = (companyId: string) => {
  const company = companies.value?.find(c => c.id === companyId)
  return company ? company.name : 'Неизвестная компания'
}

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Объявления компаний</h1>

    <!-- Search and filters -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <UInput
          v-model="search.query"
          placeholder="Поиск по названию или содержанию"
          icon="i-lucide-search"
        />
        <USelect
          v-model="search.country"
          :options="countries"
          placeholder="Все страны"
          option-attribute="id"
          clearable
        />
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="announcementsPending || companiesPending" class="bg-white rounded-lg shadow p-6">
      <ULoader class="mx-auto" />
      <p class="text-center mt-4 text-gray-500">Загрузка объявлений...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="announcementsError || companiesError" class="bg-white rounded-lg shadow p-6">
      <p class="text-red-500 text-center">
        Произошла ошибка при загрузке данных. Пожалуйста, попробуйте позже.
      </p>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredAnnouncements.length === 0" class="bg-white rounded-lg shadow p-6">
      <p class="text-center text-gray-500">
        {{ announcements && announcements.length > 0 ? 'Нет объявлений, соответствующих критериям поиска' : 'Нет доступных объявлений' }}
      </p>
    </div>

    <!-- Announcements list -->
    <div v-else class="space-y-4">
      <div v-for="announcement in filteredAnnouncements" :key="announcement.id" class="bg-white rounded-lg shadow p-6">
        <div class="flex items-start">
          <div v-if="announcement.images && announcement.images.length" class="flex-shrink-0 mr-6">
            <img :src="announcement.images[0]" alt="" class="w-24 h-24 object-cover rounded">
          </div>
          <div class="flex-grow">
            <h2 class="text-xl font-semibold">{{ announcement.title }}</h2>
            <p class="text-gray-600 mt-2">{{ announcement.content }}</p>
            <div class="flex items-center mt-4 text-sm text-gray-500">
              <span class="font-medium">{{ getCompanyName(announcement.companyId) }}</span>
              <span class="mx-2">•</span>
              <span>{{ formatDate(announcement.createdAt) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="mt-6 flex justify-center">
        <UPagination
          v-model="currentPage"
          :total="pagination.total"
          :per-page="perPage"
          :ui="{
            wrapper: 'flex items-center justify-center',
            base: 'flex items-center justify-center min-w-[32px] h-8 px-3 text-sm rounded-md',
            default: 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200',
            active: 'text-primary-500 dark:text-primary-400',
            disabled: 'opacity-50 cursor-not-allowed'
          }"
        />
      </div>
    </div>
  </div>
</template>

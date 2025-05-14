<script setup lang="ts">
import type { Company } from '~/types/company'
import type { Announcement } from '~/types/announcement'
import { useAnnouncementsApi, useCompaniesApi } from '~/api'

const { getLatestAnnouncements } = useAnnouncementsApi()
const { getLatestCompanies } = useCompaniesApi()

// Fetch announcements from API
const { data: announcements, error: announcementsError } = await getLatestAnnouncements(5)
// Fetch companies from API
const { data: companies, error: companiesError } = await getLatestCompanies(5)

// Simple helper function to get company name
const getCompanyName = (companyId: number) => {
  const company = companies.value?.find((c: Company) => c.id === companyId)
  return company?.name || 'Неизвестная компания'
}

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<template>
  <div class="space-y-8">
    <!-- Hero Section -->
    <section class="bg-[#E3D8FC] rounded-lg p-8">
      <div class="container mx-auto">
        <h1 class="text-4xl font-bold mb-4">Добро пожаловать на бизнес-платформу</h1>
        <p class="text-xl text-gray-600 mb-8">
          Найдите надежных партнеров, поставщиков и покупателей для вашего бизнеса
        </p>
        <div class="flex gap-4">
          <UButton
            to="/catalog/products"
            color="primary"
            size="xl"
          >
            Каталог товаров
          </UButton>
          <UButton
            to="/catalog/services"
            color="primary"
            variant="outline"
            size="xl"
          >
            Каталог услуг
          </UButton>
        </div>
      </div>
    </section>

    <!-- Announcements and News Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Announcements -->
      <section class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Последние объявления</h2>

        <div v-if="announcementsError" class="text-red-500 mb-4">
          Не удалось загрузить объявления
        </div>

        <div v-else-if="!announcements || announcements.length === 0" class="text-gray-500 mb-4">
          Нет доступных объявлений
        </div>

        <div v-else class="space-y-4">
          <div v-for="announcement in announcements" :key="announcement.id" class="border-b pb-4 last:border-0">
            <div class="flex items-start">
              <div v-if="announcement.images && announcement.images.length" class="flex-shrink-0 mr-4">
                <img :src="announcement.images[0]" alt="" class="w-16 h-16 object-cover rounded">
              </div>
              <div>
                <h3 class="font-medium">{{ announcement.title }}</h3>
                <p class="text-sm text-gray-600 mt-1">{{ announcement.content.substring(0, 100) }}...</p>
                <div class="flex items-center mt-2 text-xs text-gray-500">
                  <span>{{ getCompanyName(announcement.companyId) }}</span>
                  <span class="mx-2">•</span>
                  <span>{{ formatDate(announcement.createdAt) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- New Companies -->
      <section class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Новые компании</h2>

        <div v-if="companiesError" class="text-red-500 mb-4">
          Не удалось загрузить компании
        </div>

        <div v-else-if="!companies || companies.length === 0" class="text-gray-500 mb-4">
          Нет новых компаний
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="company in companies" :key="company.id" class="border rounded p-4">
            <div class="flex items-center">
              <div class="flex-shrink-0 mr-3">
                <img :src="company.logo || '/images/default-company.png'" alt="" class="w-12 h-12 object-cover rounded">
              </div>
              <div>
                <h3 class="font-medium">{{ company.name }}</h3>
                <p class="text-xs text-gray-600">{{ company.businessType }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ formatDate(company.registrationDate) }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>
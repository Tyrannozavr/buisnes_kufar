<script setup lang="ts">
import type { Company } from '~/types/company'
import { useApi } from '~/composables/useApi'

interface Announcement {
  id: string
  image: string
  title: string
  date: string
}

// Fetch announcements from API with limit
const { data: announcements, error: announcementsError } = await useApi<{
  data: Announcement[],
  pagination: {
    total: number,
    page: number,
    perPage: number,
    totalPages: number
  }
}>('/announcements?limit=5')

// Fetch companies from API
const { data: companies, error: companiesError } = await useApi<Company[]>('/companies?limit=5')

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
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Последние объявления</h2>
          <UButton
            to="/announcements"
            color="gray"
            variant="ghost"
            size="sm"
          >
            Все объявления
          </UButton>
        </div>

        <div v-if="announcementsError" class="text-red-500 mb-4">
          Не удалось загрузить объявления
        </div>

        <div v-else-if="!announcements || announcements.length === 0" class="text-gray-500 mb-4">
          Нет доступных объявлений
        </div>

        <div v-else class="space-y-4">
          <AnnouncementCard
            v-for="announcement in announcements"
            :key="announcement.id"
            :announcement="announcement"
          />
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
                <NuxtLink :to="`/company/${company.id}`" class="font-medium">{{ company.name }}</NuxtLink>
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
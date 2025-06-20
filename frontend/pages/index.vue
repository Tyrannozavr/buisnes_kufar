<script setup lang="ts">
import type { Announcement } from '~/types/announcement'
import type { Company } from '~/types/company'
import { computed } from 'vue'
import { getLatestCompaniesSSR } from '~/api/companies'
import { getLatestAnnouncementsSSR } from '~/api/announcements'

// Use SSR functions for server-side data fetching
const announcementsData = await getLatestAnnouncementsSSR(6)

// Use SSR function for companies
const response = await getLatestCompaniesSSR(6)

const companies = computed(() => response?.data || [])

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Map announcement data to match AnnouncementCard requirements
const mappedAnnouncements = computed(() => {
  if (!announcementsData?.data) return []
  
  return announcementsData.data.map((announcement: Announcement) => ({
    id: announcement.id,
    image: announcement.images?.[0] || '/images/default-announcement.png',
    title: announcement.title,
    date: announcement.date
  }))
})
</script>

<template>
  <div class="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Hero Section -->
    <section class="bg-[#E3D8FC] rounded-lg p-8 text-center">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl font-bold mb-4">Добро пожаловать на бизнес-платформу</h1>
        <p class="text-xl text-gray-600 mb-8">
          Найдите надежных партнеров, поставщиков и покупателей для вашего бизнеса
        </p>
        <div class="flex gap-4 justify-center">
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
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-semibold">Последние объявления</h2>
          <UButton
            to="/announcements"
            color="neutral"
            variant="ghost"
            size="sm"
          >
            Все объявления
          </UButton>
        </div>

        <div v-if="!mappedAnnouncements.length" class="text-gray-500 mb-4 text-center">
          Нет доступных объявлений
        </div>

        <div v-else class="space-y-4">
          <AnnouncementCard
            v-for="announcement in mappedAnnouncements"
            :key="announcement.id"
            :announcement="announcement"
          />
        </div>
      </section>

      <!-- New Companies -->
      <section class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-2xl font-semibold">Новые компании</h2>
          <UButton
            to="/companies"
            color="neutral"
            variant="ghost"
            size="sm"
          >
            Все компании
          </UButton>
        </div>

        <div v-if="!companies || companies.length === 0" class="text-gray-500 mb-4 text-center">
          Нет новых компаний
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="company in companies" :key="company.id" class="border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div class="flex items-center">
              <div class="flex-shrink-0 mr-3">

                <NuxtImg :src="company.logo_url || '/images/default-company.png'" alt="" class="w-12 h-12 object-cover rounded" />
              </div>
              <div>
                <NuxtLink :to="`/companies/${company.slug}`" class="font-medium hover:text-primary-600 transition-colors">
                  {{ company.name }}
                </NuxtLink>
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
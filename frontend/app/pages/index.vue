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
      <section>
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold">Объявления</h2>
          <UButton
            to="/announcements"
            color="primary"
            variant="ghost"
          >
            Смотреть все
          </UButton>
        </div>
        <div class="space-y-4">
          <UCard
            v-for="announcement in announcements"
            :key="announcement.id"
            class="hover:shadow-lg transition-shadow"
          >
            <template #header>
              <div class="flex items-center space-x-4">
                <img 
                  :src="getCompanyLogo(announcement.companyId)"
                  :alt="getCompanyName(announcement.companyId)"
                  class="w-10 h-10 object-contain"
                />
                <div>
                  <h3 class="font-semibold">{{ announcement.title }}</h3>
                  <p class="text-sm text-gray-500">
                    {{ getCompanyName(announcement.companyId) }}
                  </p>
                </div>
              </div>
            </template>
            <p class="text-gray-600">{{ announcement.content }}</p>
            <template #footer>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500">
                  {{ formatDate(announcement.createdAt) }}
                </span>
                <UButton
                  color="primary"
                  variant="ghost"
                  :to="`/announcements/${announcement.id}`"
                >
                  Подробнее
                </UButton>
              </div>
            </template>
          </UCard>
        </div>
      </section>

      <!-- News -->
      <section>
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold">Новости</h2>
          <UButton
            to="/news"
            color="primary"
            variant="ghost"
          >
            Смотреть все
          </UButton>
        </div>
        <div class="space-y-4">
          <UCard
            v-for="company in newCompanies"
            :key="company.id"
            class="hover:shadow-lg transition-shadow"
          >
            <template #header>
              <div class="flex items-center space-x-4">
                <img 
                  :src="company.logo"
                  :alt="company.name"
                  class="w-10 h-10 object-contain"
                />
                <div>
                  <h3 class="font-semibold">Новая компания</h3>
                  <p class="text-sm text-gray-500">{{ company.name }}</p>
                </div>
              </div>
            </template>
            <p class="text-gray-600">{{ company.description }}</p>
            <template #footer>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-500">
                  {{ formatDate(company.registrationDate) }}
                </span>
                <UButton
                  color="primary"
                  variant="ghost"
                  :to="`/companies/${company.id}`"
                >
                  Подробнее
                </UButton>
              </div>
            </template>
          </UCard>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { mockAnnouncements, mockCompanies } from '~/utils/mockData'

// Get latest announcements
const announcements = computed(() => 
  mockAnnouncements
    .filter(a => a.isPublished)
    .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
    .slice(0, 5)
)

// Get latest companies (as news)
const newCompanies = computed(() => 
  mockCompanies
    .sort((a, b) => new Date(b.registrationDate).getTime() - new Date(a.registrationDate).getTime())
    .slice(0, 5)
)

const getCompanyName = (companyId: string) => {
  const company = mockCompanies.find(c => c.id === companyId)
  return company?.name || 'Неизвестная компания'
}

const getCompanyLogo = (companyId: string) => {
  const company = mockCompanies.find(c => c.id === companyId)
  return company?.logo || '/images/default-company.png'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

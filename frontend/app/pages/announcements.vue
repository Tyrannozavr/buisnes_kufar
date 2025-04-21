<template>
  <div class="space-y-8">
    <!-- Search and Filters -->
    <section class="bg-white rounded-lg p-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UFormGroup label="Поиск">
          <UInput
            v-model="search.query"
            placeholder="Поиск по теме или содержанию"
          />
        </UFormGroup>

        <UFormGroup label="Страна">
          <USelect
            v-model="search.country"
            :options="countries"
            placeholder="Выберите страну"
          />
        </UFormGroup>

        <UFormGroup label="Дата">
          <USelect
            v-model="search.date"
            :options="dateOptions"
            placeholder="Выберите период"
          />
        </UFormGroup>
      </div>
    </section>

    <!-- Announcements List -->
    <section>
      <div class="space-y-4">
        <UCard
          v-for="announcement in filteredAnnouncements"
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

          <div class="space-y-4">
            <p class="text-gray-600">{{ announcement.content }}</p>
            
            <div v-if="announcement.images.length" class="grid grid-cols-2 md:grid-cols-3 gap-4">
              <img
                v-for="(image, index) in announcement.images"
                :key="index"
                :src="image"
                :alt="`Изображение ${index + 1}`"
                class="w-full h-32 object-cover rounded-lg"
              />
            </div>
          </div>

          <template #footer>
            <div class="flex justify-between items-center">
              <div class="flex items-center space-x-2">
                <UBadge
                  v-if="announcement.notifyPartners"
                  color="primary"
                  variant="soft"
                >
                  Партнерам
                </UBadge>
                <UBadge
                  v-if="announcement.notifySuppliers"
                  color="primary"
                  variant="soft"
                >
                  Поставщикам
                </UBadge>
                <UBadge
                  v-if="announcement.notifyBuyers"
                  color="primary"
                  variant="soft"
                >
                  Покупателям
                </UBadge>
              </div>
              <div class="flex items-center space-x-4">
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
            </div>
          </template>
        </UCard>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { mockAnnouncements, mockCompanies } from '~/utils/mockData'

// Mock data for filters
const countries = [
  'Россия',
  'Азербайджан',
  'Армения',
  'Беларусь',
  'Казахстан',
  'Кыргызстан',
  'Молдова',
  'Таджикистан',
  'Узбекистан'
]

const dateOptions = [
  'За последние 24 часа',
  'За последнюю неделю',
  'За последний месяц',
  'За последний год'
]

// Search state
const search = ref({
  query: '',
  country: '',
  date: ''
})

// Filtered announcements
const filteredAnnouncements = computed(() => {
  return mockAnnouncements
    .filter(announcement => {
      const company = mockCompanies.find(c => c.id === announcement.companyId)
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
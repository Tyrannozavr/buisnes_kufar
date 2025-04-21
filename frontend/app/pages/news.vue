<template>
  <div class="space-y-8">
    <!-- Search and Filters -->
    <section class="bg-white rounded-lg p-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UFormGroup label="Поиск">
          <UInput
            v-model="search.query"
            placeholder="Поиск по названию компании"
          />
        </UFormGroup>

        <UFormGroup label="Страна">
          <USelect
            v-model="search.country"
            :options="countries"
            placeholder="Выберите страну"
          />
        </UFormGroup>

        <UFormGroup label="Вид деятельности">
          <USelect
            v-model="search.activity"
            :options="activityTypes"
            placeholder="Выберите вид деятельности"
          />
        </UFormGroup>
      </div>
    </section>

    <!-- News List -->
    <section>
      <div class="space-y-4">
        <UCard
          v-for="company in filteredCompanies"
          :key="company.id"
          class="hover:shadow-lg transition-shadow"
        >
          <template #header>
            <div class="flex items-center space-x-4">
              <img 
                :src="company.logo"
                :alt="company.name"
                class="w-16 h-16 object-contain"
              />
              <div>
                <h3 class="text-xl font-semibold">Новая компания</h3>
                <p class="text-lg">{{ company.name }}</p>
                <p class="text-sm text-gray-500">{{ company.activity }}</p>
              </div>
            </div>
          </template>

          <div class="space-y-4">
            <p class="text-gray-600">{{ company.description }}</p>
            
            <div class="flex flex-wrap gap-2">
              <UBadge color="primary" variant="soft">
                {{ company.country }}
              </UBadge>
              <UBadge color="primary" variant="soft">
                {{ company.region }}
              </UBadge>
              <UBadge color="primary" variant="soft">
                {{ company.city }}
              </UBadge>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 class="font-semibold mb-2">Контактная информация</h4>
                <p class="text-sm text-gray-600">{{ company.phone }}</p>
                <p class="text-sm text-gray-600">{{ company.email }}</p>
                <p class="text-sm text-gray-600">{{ company.website }}</p>
              </div>
              <div>
                <h4 class="font-semibold mb-2">Адреса</h4>
                <p class="text-sm text-gray-600">{{ company.legalAddress }}</p>
                <p class="text-sm text-gray-600">{{ company.productionAddress }}</p>
              </div>
            </div>
          </div>

          <template #footer>
            <div class="flex justify-between items-center">
              <span class="text-sm text-gray-500">
                Зарегистрирована {{ formatDate(company.registrationDate) }}
              </span>
              <div class="flex space-x-2">
                <UButton
                  color="primary"
                  variant="ghost"
                  :to="`/companies/${company.id}`"
                >
                  Подробнее
                </UButton>
                <UButton
                  color="primary"
                  variant="ghost"
                  @click="$emit('send-message', company)"
                >
                  Написать
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
import type { Company } from '~/types'
import { mockCompanies } from '~/utils/mockData'

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

const activityTypes = [
  'Производство товаров',
  'Оказание услуг',
  'Производство товаров и оказание услуг'
]

// Search state
const search = ref({
  query: '',
  country: '',
  activity: ''
})

// Filtered companies
const filteredCompanies = computed(() => {
  return mockCompanies
    .filter(company => {
      const matchesQuery = !search.value.query || 
        company.name.toLowerCase().includes(search.value.query.toLowerCase()) ||
        company.activity.toLowerCase().includes(search.value.query.toLowerCase())
      
      const matchesCountry = !search.value.country || 
        company.country === search.value.country
      
      const matchesActivity = !search.value.activity || 
        company.activity === search.value.activity

      return matchesQuery && matchesCountry && matchesActivity
    })
    .sort((a, b) => new Date(b.registrationDate).getTime() - new Date(a.registrationDate).getTime())
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

defineEmits<{
  'send-message': [company: Company]
}>()
</script> 
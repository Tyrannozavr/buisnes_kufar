<script setup lang="ts">
import type {CompanyStatisticsResponse} from '~/types/company'

defineProps<CompanyStatisticsResponse>()
</script>

<template>
  <div class="mt-6">
    <UCard>
      <template #header>
        <h2 class="text-xl font-semibold">Статистика компании</h2>
      </template>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Всего продуктов -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <UIcon
            name="i-heroicons-cube"
            class="h-8 w-8 text-primary"
          />
          <div class="mt-2">
            <p class="text-sm text-gray-500">Всего продуктов</p>
            <p class="text-2xl font-semibold">{{ total_products }}</p>
          </div>
        </div>
        
        <!-- Просмотры -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <UIcon
            name="i-heroicons-eye"
            class="h-8 w-8 text-primary"
          />
          <div class="mt-2">
            <p class="text-sm text-gray-500">Просмотры</p>
            <p class="text-2xl font-semibold">{{ total_views }}</p>
            <p class="text-sm text-gray-500">
              +{{ monthly_views }} за месяц
            </p>
          </div>
        </div>

        <!-- На сайте с -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <UIcon
            name="i-heroicons-calendar"
            class="h-8 w-8 text-primary"
          />
          <div class="mt-2">
            <p class="text-sm text-gray-500">На сайте с</p>
            <p class="text-2xl font-semibold">{{ new Date(registration_date).toLocaleDateString('ru-RU', {day: 'numeric', month: 'long', year: 'numeric'}) }}</p>
          </div>
        </div>

        <!-- Закупок на сайте -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <UIcon
            name="i-heroicons-shopping-cart"
            class="h-8 w-8 text-primary"
          />
          <div class="mt-2">
            <p class="text-sm text-gray-500">Закупок на сайте</p>
<!--            <p class="text-2xl font-semibold">{{ totalPurchases || 0 }}</p>-->
            <p class="text-2xl font-semibold">В разработке...</p>
          </div>
        </div>
      </div>
    </UCard>
  </div>
</template>
<script setup lang="ts">
import type { CompanyStatistics } from '~/types/company'

defineProps<CompanyStatistics>()
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
            <p class="text-2xl font-semibold">{{ totalProducts }}</p>
          </div>
        </div>
        
        <!-- Отзывы -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <UIcon
            name="i-heroicons-chat-bubble-left-right"
            class="h-8 w-8 text-primary"
          />
          <div class="mt-2">
            <p class="text-sm text-gray-500">Отзывы</p>
            <p class="text-2xl font-semibold">{{ totalReviews }}</p>
          </div>
        </div>
        
        <!-- Средний рейтинг -->
        <div class="p-4 bg-gray-50 rounded-lg">
          <UIcon
            name="i-heroicons-star"
            class="h-8 w-8 text-primary"
          />
          <div class="mt-2">
            <p class="text-sm text-gray-500">Средний рейтинг</p>
            <div class="flex items-center">
              <p class="text-2xl font-semibold">{{ averageRating.toFixed(1) }}</p>
              <UIcon
                name="i-heroicons-star-solid"
                class="ml-1 h-5 w-5 text-yellow-400"
              />
            </div>
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
            <p class="text-2xl font-semibold">{{ totalViews }}</p>
            <p class="text-sm text-gray-500">
              +{{ monthlyViews }} за месяц
            </p>
          </div>
        </div>
      </div>
    </UCard>
  </div>
</template> 
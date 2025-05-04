<template>
  <UCard class="h-full">
    <template #header>
      <div class="flex items-center space-x-4">
        <NuxtImg
          :src="company.logo" 
          :alt="company.name"
          class="w-16 h-16 object-contain"
        />
        <div>
          <h3 class="text-lg font-semibold">{{ company.name }}</h3>
          <p class="text-sm text-gray-500">{{ company.activityType }}</p>
        </div>
      </div>
    </template>

    <div class="space-y-2">
      <p class="text-sm text-gray-600">{{ company.description }}</p>
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
    </div>

    <template #footer>
      <div class="flex justify-between items-center">
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
    </template>
  </UCard>
</template>

<script setup lang="ts">
import type { Company } from '~/types/company'

defineProps<{
  company: Company
}>()

defineEmits<{
  'send-message': [company: Company]
}>()
</script> 
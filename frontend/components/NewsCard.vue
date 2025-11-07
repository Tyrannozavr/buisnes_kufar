<script setup lang="ts">
import type { NewsItem } from '~/types/news'

defineProps<{
  item: NewsItem
}>()
</script>

<template>
  <UCard class="hover:shadow-lg transition-shadow">
    <template #header>
      <div class="flex items-center space-x-4">
        <NuxtImg
          :src="item.companyLogo"
          :alt="item.title"
          class="w-16 h-16 object-cover rounded-lg"
        />
        <div>
          <h2 class="text-xl font-semibold">
            <NuxtLink v-if="item.companySlug" :to="`/companies/${item.companySlug}`" class="hover:text-primary-500">
              {{ item.title }}
            </NuxtLink>
            <span v-else>{{ item.title }}</span>
          </h2>
          <p class="text-sm text-gray-500">{{ new Date(item.date).toLocaleDateString() }}</p>
          <p class="text-sm text-gray-600">{{ item.activityType }}</p>
        </div>
      </div>
    </template>

    <div class="space-y-4">
      <p class="text-gray-600">{{ item.content }}</p>
    </div>

    <template #footer>
      <div v-if="item.companySlug" class="flex justify-end">
        <UButton
          color="primary"
          variant="ghost"
          :to="`/companies/${item.companySlug}`"
        >
          Перейти к компании
        </UButton>
      </div>
    </template>
  </UCard>
</template> 
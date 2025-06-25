<script setup lang="ts">
import { usePublicAnnouncementsApi } from '~/api/announcements'

const route = useRoute()
const id = parseInt(route.params.id as string)

const { getAnnouncementById } = usePublicAnnouncementsApi()

const { data: announcement, error, pending } = await useAsyncData(`announcement-${id}`, () => getAnnouncementById(id))

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  });
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading state -->
    <div v-if="pending" class="max-w-4xl mx-auto">
      <p class="text-center text-gray-500">
        Загрузка объявления...
      </p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="max-w-4xl mx-auto">
      <p class="text-center text-red-500">
        Произошла ошибка при загрузке объявления. Пожалуйста, попробуйте позже.
      </p>
    </div>

    <!-- Announcement content -->
    <article v-else-if="announcement" class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <!-- Content -->
        <div class="p-6">
          <h1 class="text-3xl font-bold mb-4">{{ announcement.title }}</h1>
          <p class="text-gray-500 mb-6">{{ formatDate(announcement.created_at) }}</p>
          <div class="prose max-w-none mb-6">
            <p class="whitespace-pre-wrap">{{ announcement.content }}</p>
          </div>
          <!-- Images -->
          <div v-if="announcement.image_urls && announcement.image_urls.length > 0" class="mt-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <NuxtImg
                v-for="(imageUrl, index) in announcement.image_urls"
                :key="index"
                :src="imageUrl"
                :alt="`${announcement.title} - изображение ${index + 1}`"
                class="w-full rounded-lg shadow-md"
              />
            </div>
          </div>
          <!-- Company info -->
          <div v-if="announcement.company" class="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 class="text-lg font-semibold mb-2">Компания</h3>
            <div class="flex items-center space-x-3">
              <NuxtImg
                v-if="announcement.company.logo_url"
                :src="announcement.company.logo_url"
                :alt="announcement.company.name"
                class="w-12 h-12 rounded-full object-cover"
              />
              <div>
                <p class="font-medium">{{ announcement.company.name }}</p>
                <p class="text-sm text-gray-500">Категория: {{ announcement.category }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </article>
  </div>
</template>
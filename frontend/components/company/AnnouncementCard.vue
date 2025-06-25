<script setup lang="ts">
import { useRouter } from 'vue-router';
import type { Announcement } from '~/types/announcement';

const props = defineProps<{
  announcement: Announcement,
  getStatusColor: (published: boolean) => string,
  getStatusLabel: (published: boolean) => string,
  formatDate: (date: string) => string
}>();

const emit = defineEmits(['publish', 'delete']);
const router = useRouter();
</script>

<template>
  <UCard class="overflow-hidden px-3 py-3 md:px-2 md:py-2 mx-auto announcement-card">
    <div class="flex flex-col md:flex-row gap-2 md:gap-2 announcement-card-inner">
      <div 
        v-if="announcement.images && announcement.images.length > 0" 
        class="announcement-image w-full md:w-20 h-32 md:h-16 flex-shrink-0 cursor-pointer"
        @click="router.push(`/announcements/${announcement.id}`)"
      >
        <NuxtImg :src="announcement.image_urls[0]" alt="Изображение объявления" class="w-full h-full object-cover rounded-md" />
      </div>
      <div v-else class="announcement-image w-full md:w-20 h-32 md:h-16 flex-shrink-0 bg-gray-100 flex items-center justify-center rounded-md">
        <UIcon name="i-heroicons-photo" class="h-10 w-10 text-gray-400" />
      </div>

      <div class="flex-1">
        <div class="flex justify-between items-start">
          <h3 
            class="text-base md:text-md font-semibold cursor-pointer hover:text-primary-500"
            @click="router.push(`/profile/announcements/${announcement.id}`)"
          >{{ announcement.title }}</h3>
          <UBadge :color="props.getStatusColor(announcement.published) as 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'error' | 'neutral'">
            {{ props.getStatusLabel(announcement.published) }}
          </UBadge>
        </div>

        <UBadge class="mt-2" color="neutral" variant="subtle">
          {{ announcement.category }}
        </UBadge>

        <p class="mt-2 text-sm text-gray-600 line-clamp-2 md:line-clamp-1">{{ announcement.content }}</p>

        <div class="mt-3 flex justify-between items-center">
          <div class="text-xs text-gray-500">
            Создано: {{ props.formatDate(announcement.created_at) }}
          </div>

          <div class="flex gap-2">
            <UButton
              v-if="!announcement.published"
              size="sm"
              color="primary"
              class="cursor-pointer"
              @click="emit('publish', announcement)"
            >
              Опубликовать
            </UButton>
            <UButton
              v-else
              size="sm"
              color="warning"
              variant="soft"
              class="cursor-pointer"
              @click="emit('publish', announcement)"
            >
              Снять с публикации
            </UButton>
            <UButton
              size="sm"
              color="neutral"
              variant="soft"
              :to="`/profile/announcements/${announcement.id}`"
            >
              Просмотр
            </UButton>
            <UButton
              size="sm"
              color="neutral"
              variant="soft"
              :to="`/profile/announcements/edit/${announcement.id}`"
            >
              Редактировать
            </UButton>
            <UButton
              size="sm"
              color="error"
              variant="soft"
              class="cursor-pointer"
              @click="emit('delete', announcement)"
            >
              Удалить
            </UButton>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>

<style scoped>
@media (min-width: 768px) and (max-width: 1024px) {
  .announcement-card {
    max-width: 400px !important;
    margin-left: auto;
    margin-right: auto;
    padding-left: 8px !important;
    padding-right: 8px !important;
    padding-top: 8px !important;
    padding-bottom: 8px !important;
  }
  .announcement-card-inner {
    flex-direction: column !important;
    gap: 8px !important;
  }
  .announcement-image {
    width: 100% !important;
    height: 120px !important;
    min-height: 80px;
    max-height: 140px;
    margin-bottom: 4px;
  }
}
</style> 
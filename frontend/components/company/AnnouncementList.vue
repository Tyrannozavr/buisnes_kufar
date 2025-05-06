<script setup lang="ts">
import type { Announcement } from '~/types/announcement'

defineProps<{
  announcements: Announcement[] | null
  loading: boolean
}>()

const emit = defineEmits<{
  publish: [id: string]
}>()

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const getStatusColor = (published: boolean) => {
  if (published) {
    return 'success'
  } else {
    return 'neutral'
  }
}

const getStatusLabel = (published: boolean) => {
  if (published) {
    return 'Опубликовано'
  } else {
    return 'Черновик'
  }
}

const getCategoryLabel = (category: string) => {
  switch (category) {
    case 'product':
      return 'Продукция'
    case 'promotion':
      return 'Акция'
    case 'partnership':
      return 'Партнерство'
    default:
      return category
  }
}
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">Объявления компании</h2>
      <UButton
        icon="i-heroicons-plus"
        color="primary"
        to="/profile/announcements/create"
      >
        Создать объявление
      </UButton>
    </div>

    <UCard v-if="loading">
      <div class="flex justify-center py-8">
        <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
      </div>
    </UCard>

    <template v-else-if="announcements && announcements.length > 0">
      <div class="space-y-4">
        <UCard v-for="announcement in announcements" :key="announcement.id" class="overflow-hidden">
          <div class="flex flex-col md:flex-row gap-4">
            <div v-if="announcement.images && announcement.images.length > 0" class="w-full md:w-48 h-32 flex-shrink-0">
              <NuxtImg :src="announcement.images[0]" alt="Изображение объявления" class="w-full h-full object-cover rounded-md" />
            </div>
            <div v-else class="w-full md:w-48 h-32 flex-shrink-0 bg-gray-100 flex items-center justify-center rounded-md">
              <UIcon name="i-heroicons-photo" class="h-12 w-12 text-gray-400" />
            </div>

            <div class="flex-1">
              <div class="flex justify-between items-start">
                <h3 class="text-lg font-semibold">{{ announcement.title }}</h3>
                <UBadge :color="getStatusColor(announcement.published)">
                  {{ getStatusLabel(announcement.published) }}
                </UBadge>
              </div>

              <UBadge class="mt-2" color="neutral" variant="subtle">
                {{ getCategoryLabel(announcement.category) }}
              </UBadge>

              <p class="mt-2 text-sm text-gray-600 line-clamp-2">{{ announcement.content }}</p>

              <div class="mt-4 flex justify-between items-center">
                <div class="text-xs text-gray-500">
                  Создано: {{ formatDate(announcement.createdAt) }}
                </div>

                <div class="flex gap-2">
                  <UButton
                    v-if="!announcement.published"
                    size="sm"
                    color="primary"
                    class="cursor-pointer"
                    @click="emit('publish', announcement.id)"
                  >
                    Опубликовать
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
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </template>

    <UCard v-else>
      <div class="py-8 text-center">
        <UIcon name="i-heroicons-megaphone" class="h-12 w-12 mx-auto text-gray-400" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">У вас пока нет объявлений</h3>
        <p class="mt-2 text-sm text-gray-500">
          Создайте свое первое объявление, чтобы рассказать о своих товарах или услугах
        </p>
        <div class="mt-6">
          <UButton
            color="primary"
            to="/profile/announcements/create"
          >
            Создать объявление
          </UButton>
        </div>
      </div>
    </UCard>
  </div>
</template>
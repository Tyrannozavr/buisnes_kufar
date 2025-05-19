<script setup lang="ts">
interface DetailedAnnouncement {
  id: string
  image: string
  title: string
  date: string
  content: string
}

const route = useRoute()
const id = route.params.id

const { data: announcement, error, pending } = await useApi<DetailedAnnouncement>(`/announcements/${id}`)

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
          <p class="text-gray-500 mb-6">{{ formatDate(announcement.date) }}</p>
          <div class="prose max-w-none mb-6">
            <p class="whitespace-pre-wrap">{{ announcement.content }}</p>
          </div>
          <!-- Image -->
          <div v-if="announcement.image" class="mt-6">
            <NuxtImg
              :src="announcement.image"
              :alt="announcement.title"
              class="w-full max-w-md mx-auto rounded-lg shadow-md"
            />
          </div>
        </div>
      </div>
    </article>
  </div>
</template>
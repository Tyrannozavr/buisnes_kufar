<script setup lang="ts">
import { usePublicAnnouncementsApi } from '~/api/announcements'

const currentPage = ref(1)
const perPage = ref(10)

const { getAllAnnouncements } = usePublicAnnouncementsApi()

// Используем ref вместо useAsyncData для прямого контроля над запросами
const response = ref(null)
const announcementsError = ref(null)
const announcementsPending = ref(true)

const loadAnnouncements = async () => {
  try {
    announcementsPending.value = true
    announcementsError.value = null
    response.value = await getAllAnnouncements(currentPage.value, perPage.value)
  } catch (error) {
    announcementsError.value = error
  } finally {
    announcementsPending.value = false
  }
}

// Загружаем данные при монтировании
await loadAnnouncements()

const announcements = computed(() => response.value?.announcements || [])
const pagination = computed(() => ({
  total: response.value?.total || 0,
  page: response.value?.page || 1,
  perPage: response.value?.per_page || 10,
  totalPages: Math.ceil((response.value?.total || 0) / perPage.value)
}))

// Watch for page changes
watch(currentPage, async (newPage) => {
  await loadAnnouncements()
})

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
  <div class="container mx-auto">
    <h1 class="text-3xl font-bold mb-8">Объявления</h1>
    <div class="space-y-8">
      <!-- Loading state -->
      <section v-if="announcementsPending" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-gray-500">
          Загрузка объявлений...
        </p>
      </section>

      <!-- Error state -->
      <section v-else-if="announcementsError" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-red-500">
          Произошла ошибка при загрузке объявлений. Пожалуйста, попробуйте позже.
        </p>
      </section>

      <!-- Empty state -->
      <section v-else-if="announcements.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
        <p class="text-center text-gray-500">
          На данный момент объявлений нет.
        </p>
      </section>

      <!-- Announcements List -->
      <section v-else>
        <div class="space-y-4">
          <div
              v-for="announcement in announcements"
              :key="announcement.id"
              class="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer flex px-2"
              @click="announcement.id && navigateTo(`/announcements/${announcement.id}`)"
          >
            <div class="w-24 h-24 flex-shrink-0">
              <NuxtImg
                :src="announcement.image_url || '/default-announcement.jpg'" 
                :alt="announcement.title"
                class="w-full h-full object-cover rounded-l-lg"
              />
            </div>
            <div class="p-4 flex-1">
              <h2 class="text-lg font-semibold mb-2 line-clamp-2">{{ announcement.title }}</h2>
              <p class="text-sm text-gray-500">{{ formatDate(announcement.created_at) }}</p>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div class="mt-6 flex justify-center">
          <UPagination
              v-model="currentPage"
              :total="pagination.total"
              :per-page="perPage"
          />
        </div>
      </section>
    </div>
  </div>
</template>
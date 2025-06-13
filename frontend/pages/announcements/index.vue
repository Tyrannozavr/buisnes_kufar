<script setup lang="ts">
import { useAnnouncements } from '~/api/announcements'

const currentPage = ref(1)
const perPage = ref(10)

const { data: response, error: announcementsError, pending: announcementsPending, refresh: refreshAnnouncements }
    = useAnnouncements(currentPage.value, perPage.value)
console.log('Announcements:', response.value)
const announcements = computed(() => response.value?.data || [])
const pagination = computed(() => response.value?.pagination || {
  total: 0,
  page: 1,
  perPage: 10,
  totalPages: 1
})

// Watch for page changes
watch(currentPage, async (newPage) => {
  await refreshAnnouncements()
})
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
          <AnnouncementCard
              v-for="announcement in announcements"
              :key="announcement.id"
              :announcement="announcement"
          />
        </div>

        <!-- Pagination -->
        <div class="mt-6 flex justify-center">
          <UPagination
              v-model="currentPage"
              :total="pagination.total"
              :per-page="perPage"
              :ui="{
              base: 'flex items-center justify-center min-w-[32px] h-8 px-3 text-sm rounded-md',
              default: 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200',
              active: 'text-primary-500 dark:text-primary-400',
              disabled: 'opacity-50 cursor-not-allowed'
            }"
          />
        </div>
      </section>
    </div>
  </div>
</template>
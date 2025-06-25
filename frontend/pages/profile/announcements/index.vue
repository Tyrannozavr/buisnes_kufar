<script setup lang="ts">
import type { Announcement } from '~/types/announcement'
import AnnouncementList from '~/components/company/AnnouncementList.vue'
import { useAnnouncementsApi } from '~/api/me/announcements'

definePageMeta({
  layout: 'profile'
})

const currentPage = ref(1)
const perPage = ref(10)

const { getAnnouncements, deleteAnnouncement } = useAnnouncementsApi()

const { data: announcementsData, pending: loadingAnnouncements, refresh: refreshAnnouncements } = await useAsyncData(
  'announcements',
  () => getAnnouncements(currentPage.value, perPage.value),
  { watch: [currentPage, perPage] }
)

const formattedAnnouncements = computed(() => {
  if (!announcementsData.value) return null
  
  return {
    data: announcementsData.value.announcements,
    pagination: {
      total: announcementsData.value.total,
      page: announcementsData.value.page,
      perPage: announcementsData.value.per_page,
      totalPages: Math.ceil(announcementsData.value.total / announcementsData.value.per_page)
    }
  }
})

const handlePageChange = (page: number) => {
  currentPage.value = page
  refreshAnnouncements()
}

const showDeleteConfirm = ref(false)
const selectedAnnouncement = ref<Announcement | null>(null)
const processingDelete = ref(false)

const handleDeleteAnnouncement = (announcement: Announcement) => {
  selectedAnnouncement.value = announcement
  showDeleteConfirm.value = true
}

const confirmDelete = async () => {
  if (!selectedAnnouncement.value) return
  
  processingDelete.value = true
  try {
    await deleteAnnouncement(selectedAnnouncement.value.id)
    await refreshAnnouncements()
    useToast().add({
      title: 'Успешно',
      description: 'Объявление удалено',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось удалить объявление',
      color: 'error'
    })
  } finally {
    processingDelete.value = false
    showDeleteConfirm.value = false
    selectedAnnouncement.value = null
  }
}

const cancelDelete = () => {
  showDeleteConfirm.value = false
  selectedAnnouncement.value = null
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <AnnouncementList
        :announcements="formattedAnnouncements"
        :loading="loadingAnnouncements"
        @delete="handleDeleteAnnouncement"
        @page-change="handlePageChange"
      />
    </div>

    <UModal v-model:open="showDeleteConfirm" title="Подтверждение удаления">
      <template #body>
        <div class="p-4">
          <p class="text-gray-600 mb-4">
            Вы действительно хотите удалить объявление "{{ selectedAnnouncement?.title }}"?
            Это действие нельзя будет отменить.
          </p>
          <div class="flex justify-end gap-2">
            <UButton
              color="neutral"
              variant="outline"
              @click="cancelDelete"
            >
              Отмена
            </UButton>
            <UButton
              color="error"
              :loading="processingDelete"
              @click="confirmDelete"
            >
              Удалить
            </UButton>
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>
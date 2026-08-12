<script setup lang="ts">
import type { Announcement } from '~/types/announcement'
import AnnouncementList from '~/components/company/AnnouncementList.vue'
import { useAnnouncementsApi } from '~/api/me/announcements'

definePageMeta({
  layout: 'profile'
})

const currentPage = ref(1)
const perPage = ref(10)

const { getAnnouncements, deleteAnnouncement, toggleAnnouncementPublish } = useAnnouncementsApi()

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

const {
  deleteOpen,
  deleteLoading,
  deleteTitle,
  deleteMessage,
  askDelete,
  confirmDelete,
} = useConfirmDelete()

const handleDeleteAnnouncement = (announcement: Announcement) => {
  askDelete({
    message: `Точно хотите удалить объявление «${announcement.title}»?\nЭто действие нельзя отменить.`,
    onConfirm: async () => {
      try {
        await deleteAnnouncement(announcement.id)
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
        throw e
      }
    },
  })
}

const handlePublishAnnouncement = async (announcementId: string) => {
  try {
    await toggleAnnouncementPublish(parseInt(announcementId))
    await refreshAnnouncements()
    useToast().add({
      title: 'Успешно',
      description: 'Статус объявления изменен',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось изменить статус объявления',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <AnnouncementList
        :announcements="formattedAnnouncements"
        :loading="loadingAnnouncements"
        @delete="handleDeleteAnnouncement"
        @publish="handlePublishAnnouncement"
        @page-change="handlePageChange"
      />
    </div>

    <ConfirmDeleteModal
      v-model:open="deleteOpen"
      :title="deleteTitle"
      :message="deleteMessage"
      :loading="deleteLoading"
      @confirm="confirmDelete"
    />
  </div>
</template>

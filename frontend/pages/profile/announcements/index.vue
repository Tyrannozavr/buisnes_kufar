<script setup lang="ts">
import type { Announcement } from '~/types/announcement'
import AnnouncementList from '~/components/company/AnnouncementList.vue'
import { useAnnouncementsApi } from '~/api'

definePageMeta({
  layout: 'profile'
})

const currentPage = ref(1)
const perPage = ref(10)

const { getCompanyAnnouncements, publishAnnouncement: publishAnnouncementApi } = useAnnouncementsApi()

const {
  data: announcements,
  pending: loadingAnnouncements,
  refresh: refreshAnnouncements,
} = await getCompanyAnnouncements(currentPage.value, perPage.value)

const handlePageChange = (page: number) => {
  currentPage.value = page
  refreshAnnouncements()
}

const publishAnnouncement = async (announcement: Announcement) => {
  try {
    await publishAnnouncementApi(announcement.id)
    await refreshAnnouncements()
    useToast().add({
      title: 'Успешно',
      description: 'Объявление опубликовано',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось опубликовать объявление',
      color: 'error'
    })
  }
}
</script>

<template>
  <ProfileLayout>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Объявления</h2>
      <AnnouncementList
        :announcements="announcements || null"
        :loading="loadingAnnouncements"
        @publish="publishAnnouncement"
        @page-change="handlePageChange"
      />
    </div>
  </ProfileLayout>
</template> 
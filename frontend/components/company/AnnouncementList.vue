<script setup lang="ts">
import type { Announcement } from '~/types/announcement'
import PublishConfirmModal from '~/components/announcement/PublishConfirmModal.vue';
import { useRouter } from 'vue-router'
import AnnouncementCard from './AnnouncementCard.vue';

defineProps<{
  announcements: {
    data: Announcement[],
    pagination: {
      total: number,
      page: number,
      perPage: number,
      totalPages: number
    }
  } | null
  loading: boolean
}>()

const router = useRouter()

const emit = defineEmits<{
  publish: [id: string]
  delete: [announcement: Announcement]
  pageChange: [page: number]
}>()

// Состояние для модального окна
const showPublishConfirm = ref(false)
const selectedAnnouncementId = ref<string | null>(null)
const selectedAnnouncement = ref<Announcement | null>(null)
const processingPublish = ref(false)

// Состояние для опций уведомлений
const notifyOptions = ref({
  notify: false,
  partners: false,
  customers: false,
  suppliers: false
})

// Pagination state
const currentPage = ref(1)
const perPage = ref(10)

// Watch for page changes
watch(currentPage, (newPage) => {
  emit('pageChange', newPage)
})

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

// Функция для открытия модального окна подтверждения публикации
const openPublishConfirm = (announcement: Announcement) => {
  selectedAnnouncementId.value = announcement.id.toString()
  selectedAnnouncement.value = announcement

  // Установка опций уведомлений из объявления, если они есть
  if (announcement.notifications) {
    notifyOptions.value.notify = true
    notifyOptions.value.partners = announcement.notifications.partners
    notifyOptions.value.customers = announcement.notifications.customers
    notifyOptions.value.suppliers = announcement.notifications.suppliers
  } else {
    // Значения по умолчанию, если уведомления не настроены
    notifyOptions.value.notify = false
    notifyOptions.value.partners = false
    notifyOptions.value.customers = false
    notifyOptions.value.suppliers = false
  }

  showPublishConfirm.value = true
}

// Функция для закрытия модального окна
const closePublishModal = () => {
  showPublishConfirm.value = false
  selectedAnnouncementId.value = null
  selectedAnnouncement.value = null
}

// Функция для подтверждения публикации
const confirmPublish = () => {
  if (selectedAnnouncementId.value) {
    processingPublish.value = true
    emit('publish', selectedAnnouncementId.value)
    processingPublish.value = false
    closePublishModal()
  }
}

// Функция для удаления объявления
const handleDelete = (announcement: Announcement) => {
  emit('delete', announcement)
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

    <template v-else-if="announcements?.data && announcements.data.length > 0">
      <div class="space-y-4">
        <AnnouncementCard
          v-for="announcement in announcements.data"
          :key="announcement.id"
          :announcement="announcement"
          :get-status-color="getStatusColor"
          :get-status-label="getStatusLabel"
          :format-date="formatDate"
          @publish="openPublishConfirm"
          @delete="handleDelete"
        />
        <!-- Pagination -->
        <div class="mt-6 flex justify-center">
          <UPagination
            v-model="currentPage"
            :total="announcements.pagination.total"
            :per-page="perPage"
          />
        </div>
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

    <!-- Модальное окно подтверждения публикации -->
    <PublishConfirmModal
      :open="showPublishConfirm"
      :saving="processingPublish"
      :is-publishing="!selectedAnnouncement?.published"
      :notify-options="notifyOptions"
      @close="closePublishModal"
      @confirm="confirmPublish"
    />
  </div>
</template>
<script setup lang="ts">
import {ref} from 'vue';
import { useAnnouncementsApi } from '~/api/me/announcements'

const route = useRoute();
const router = useRouter();
const id = parseInt(route.params.id as string);

const {
  getAnnouncementById,
  deleteAnnouncement
} = useAnnouncementsApi()

const {
  data: announcement,
  error: fetchError,
  pending: loading,
  refresh
} = await useAsyncData(`announcement-${id}`, () => getAnnouncementById(id));

const processingAction = ref(false);
const showDeleteConfirm = ref(false);

// Format date for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

// Handle deleting announcement
const handleDeleteAnnouncement = async () => {
  processingAction.value = true;
  try {
    await deleteAnnouncement(id);

    useToast().add({
      title: 'Успешно',
      description: 'Объявление удалено',
      color: 'success'
    });

    // Redirect back to announcements list
    router.push('/profile/announcements');
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: error instanceof Error ? error.message : 'Не удалось удалить объявление',
      color: 'error'
    });
  } finally {
    processingAction.value = false;
    showDeleteConfirm.value = false;
  }
};

// Navigate to edit page
const editAnnouncement = () => {
  router.push(`/profile/announcements/edit/${id}`);
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <UBreadcrumb
        :items="[
      { label: 'Профиль', to: '/profile' },
      { label: 'Объявления', to: '/profile/announcements' },
      { label: announcement?.title || 'Загрузка...', to: '' }
    ]" class="mb-6"/>
    <template v-if="loading">
      <UCard>
        <div class="flex justify-center p-8">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500"/>
        </div>
      </UCard>
    </template>

    <template v-else-if="fetchError">
      <UAlert
          color="error"
          title="Ошибка загрузки объявления"
          :description="fetchError.toString()"
          icon="i-heroicons-exclamation-circle"
      >
        <template #footer>
          <UButton
              color="error"
              variant="ghost"
              to="/profile/announcements"
          >
            Вернуться к объявлениям
          </UButton>
        </template>
      </UAlert>
    </template>

    <template v-else-if="!announcement">
      <UAlert
          color="warning"
          title="Объявление не найдено"
          description="Запрашиваемое объявление не существует или было удалено"
          icon="i-heroicons-exclamation-triangle"
      >
        <template #footer>
          <UButton
              color="warning"
              variant="ghost"
              to="/profile/announcements"
          >
            Вернуться к объявлениям
          </UButton>
        </template>
      </UAlert>
    </template>

    <template v-else>
      <UCard>
        <template #header>
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-2xl font-bold">{{ announcement.title }}</h1>
              <div class="flex items-center mt-2 text-sm text-gray-500">
                <UIcon name="i-heroicons-calendar" class="mr-1"/>
                <span>Создано: {{ formatDate(announcement.created_at) }}</span>
                <span class="mx-2">•</span>
                <UIcon name="i-heroicons-clock" class="mr-1"/>
                <span>Обновлено: {{ formatDate(announcement.updated_at) }}</span>
              </div>
            </div>
            <UBadge :color="announcement.published ? 'success' : 'neutral'">
              {{ announcement.published ? 'Опубликовано' : 'Черновик' }}
            </UBadge>
          </div>
        </template>

        <!-- Announcement content -->
        <div class="space-y-6">
          <!-- Images gallery -->
          <div v-if="announcement.image_urls && announcement.image_urls.length" class="mb-6">
            <UCarousel :items="announcement.image_urls.map(img => ({ src: img }))" class="rounded-lg overflow-hidden">
              <template #default="{ item }">
                <NuxtImg :src="item.src" class="w-full h-64 object-contain bg-gray-100"/>
              </template>
            </UCarousel>
          </div>

          <!-- Content -->
          <div class="prose max-w-none">
            <p>{{ announcement.content }}</p>
          </div>
        </div>

        <template #footer>
          <div class="flex justify-between">
            <UButton
                color="neutral"
                variant="ghost"
                to="/profile/announcements"
                icon="i-heroicons-arrow-left"
            >
              Назад к списку
            </UButton>

            <div class="flex gap-2">
              <UButton
                  v-if="!announcement.published"
                  color="primary"
                  icon="i-heroicons-pencil"
                  class="cursor-pointer"
                  @click="editAnnouncement"
              >
                Редактировать
              </UButton>

              <UButton
                  color="error"
                  icon="i-heroicons-trash"
                  :loading="processingAction"
                  class="cursor-pointer"
                  @click="showDeleteConfirm = true"
              >
                Удалить
              </UButton>
            </div>
          </div>
        </template>
      </UCard>
      <!-- Delete confirmation modal -->
      <UModal v-model:open="showDeleteConfirm" title="Подтверждение удаления">
        <template #body>
          <div class="p-4">
            <p class="text-gray-600 mb-4">
              Вы действительно хотите удалить объявление "{{ announcement.title }}"?
              Это действие нельзя будет отменить.
            </p>
            <div class="flex justify-end gap-2 ">
              <UButton
                  color="neutral"
                  variant="outline"
                  @click="showDeleteConfirm = false"
              >
                Отмена
              </UButton>
              <UButton
                  color="error"
                  :loading="processingAction"
                  @click="handleDeleteAnnouncement"
              >
                Удалить
              </UButton>
            </div>
          </div>
        </template>
      </UModal>
    </template>
  </div>
</template>
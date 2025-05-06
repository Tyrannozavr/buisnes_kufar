<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Announcement } from '~/types/announcement';

const route = useRoute();
const router = useRouter();
const id = route.params.id as string;

const saving = ref(false);
const { data: announcement, error: fetchError, pending: loading } = await useApi<Announcement>(`/announcements/${id}`);

// Check if announcement exists and is not published
const canEdit = computed(() => {
  return announcement.value && !announcement.value.published;
});

// Initial form data
const initialFormData = computed(() => {
  if (!announcement.value) return null;

  return {
    title: announcement.value.title,
    content: announcement.value.content,
    images: [...announcement.value.images]
  };
});

const handleSave = async (formData, publish = false) => {
  saving.value = true;
  try {
    await useApi(`/announcements/${id}`, {
      method: 'PUT',
      body: {
        ...formData,
        published: publish
      }
    });

    useToast().add({
      title: 'Успешно',
      description: publish ? 'Объявление обновлено и опубликовано' : 'Объявление обновлено',
      color: 'success'
    });

    // errorirect back to announcement view
    router.push(`/profile/announcements/${id}`);
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: error instanceof Error ? error.message : 'Не удалось обновить объявление',
      color: 'error'
    });
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  router.push(`/profile/announcements/${id}`);
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <UBreadcrumb
:items="[
      { label: 'Профиль', to: '/profile' },
      { label: 'Объявления', to: '/profile?section=announcements' },
      { label: announcement?.title || 'Загрузка...', to: `/profile/announcements/${id}` },
      { label: 'Редактирование', to: '' }
    ]" class="mb-6" />

    <template v-if="loading">
      <UCard>
        <div class="flex justify-center p-8">
          <UIcon name="i-heroicons-arrow-path" class="animate-spin h-8 w-8 text-gray-500" />
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
            to="/profile"
          >
            Вернуться к профилю
          </UButton>
        </template>
      </UAlert>
    </template>

    <template v-else-if="!canEdit">
      <UAlert
        color="warning"
        title="Редактирование недоступно"
        description="Объявление не найдено или уже опубликовано"
        icon="i-heroicons-exclamation-triangle"
      >
        <template #footer>
          <UButton
            color="warning"
            variant="ghost"
            to="/profile"
          >
            Вернуться к профилю
          </UButton>
        </template>
      </UAlert>
    </template>

    <template v-else>
      <AnnouncementForm
        :initial-data="initialFormData || undefined"
        :loading="saving"
        :is-edit="true"
        @save="handleSave"
        @cancel="handleCancel"
      />
    </template>
  </div>
</template>
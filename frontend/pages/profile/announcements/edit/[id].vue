<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Announcement, AnnouncementFormData } from '~/types/announcement';
import type {Category} from "~/types/category";
import { useAnnouncementsApi } from '~/api'
import { useCategoriesApi } from '~/api'

const route = useRoute();
const router = useRouter();
const id = route.params.id as string;

const saving = ref(false);
const { getAnnouncementById, updateAnnouncement } = useAnnouncementsApi()
const { getCategories } = useCategoriesApi()

// Fetch announcement data
const { data: announcement, error: fetchError, pending: loading } = await getAnnouncementById(id);

// Check if announcement exists and is not published
const canEdit = computed(() => {
  return announcement.value && !announcement.value.published;
});

// Initial form data
const initialFormData = computed<AnnouncementFormData>(() => {
  if (!announcement.value) {
    return {
      title: '',
      content: '',
      images: [],
      category: ''
    };
  }

  return {
    title: announcement.value.title,
    content: announcement.value.content,
    images: announcement.value.images || [],
    category: announcement.value.category,
  };
});

// Fetch categories from API
const { data: categories, error: categoriesError } = await getCategories()

const handleSave = async (formData: AnnouncementFormData, publish = false) => {
  saving.value = true;
  try {
    await updateAnnouncement(id, {
      ...formData,
      published: publish
    });

    useToast().add({
      title: 'Успешно',
      description: publish ? 'Объявление обновлено и опубликовано' : 'Объявление обновлено',
      color: 'success'
    });

    // Redirect back to announcement view
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
        { label: 'Объявления', to: '/profile/announcements' },
        { label: announcement?.title || 'Загрузка...', to: `/profile/announcements/${id}` },
        { label: 'Редактирование', to: '' }
      ]"
      class="mb-6"
    />

    <template v-if="loading">
      <PageLoader text="Загрузка объявления..." />
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

    <template v-else-if="categoriesError">
      <UAlert
        color="error"
        title="Ошибка загрузки категорий"
        :description="categoriesError.toString()"
        icon="i-heroicons-exclamation-circle"
      />
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
            to="/profile/announcements"
          >
            Вернуться к объявлениям
          </UButton>
        </template>
      </UAlert>
    </template>

    <template v-else>
      <AnnouncementForm
        :initial-data="initialFormData"
        :loading="saving"
        :categories="categories"
        :is-edit="true"
        @save="handleSave"
        @cancel="handleCancel"
      />
    </template>
  </div>
</template>
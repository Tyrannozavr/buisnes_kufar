<script setup lang="ts">
import type { AnnouncementFormData } from '~/types/announcement';
import type { Category } from '~/types/category';

const router = useRouter();
const saving = ref(false);
const formTouched = ref(false);

const form = ref<AnnouncementFormData>({
  title: '',
  content: '',
  images: [],
  category: ''
});

// Fetch categories from API
const { data: categories, error: categoriesError } = await useApi<Category[]>('/categories');
// Store object URLs to revoke them later
const objectUrls = ref<string[]>([]);

// Clean up object URLs when component is unmounted
onBeforeUnmount(() => {
  objectUrls.value.forEach(url => URL.revokeObjectURL(url));
});

const handleSave = async (formData: AnnouncementFormData, publish = false) => {
  formTouched.value = true;
  saving.value = true;
  try {
    await useApi('/announcements', {
      method: 'POST',
      body: {
        ...formData,
        published: publish
      }
    });

    useToast().add({
      title: 'Успешно',
      description: publish ? 'Объявление создано и опубликовано' : 'Объявление сохранено как черновик',
      color: 'success'
    });

    // Redirect back to announcements list
    router.push('/profile?section=announcements');
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: error instanceof Error ? error.message : 'Не удалось создать объявление',
      color: 'error'
    });
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  router.push('/profile?section=announcements');
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <UBreadcrumb
      :items="[
        { label: 'Профиль', to: '/profile' },
        { label: 'Объявления', to: '/profile?section=announcements' },
        { label: 'Создание объявления', to: '' }
      ]"
      class="mb-6"
    />

    <div v-if="categoriesError" class="mb-6">
      <UAlert
        color="error"
        title="Ошибка загрузки категорий"
        :description="categoriesError instanceof Error ? categoriesError.message : 'Не удалось загрузить категории'"
        icon="i-heroicons-exclamation-circle"
      />
    </div>

    <div v-else-if="!categories">
      <PageLoader text="Загрузка категорий..." />
    </div>

    <div v-else>
      <AnnouncementForm
        :loading="saving"
        :is-edit="false"
        :categories="categories"
        :initial-data="form"
        @save="handleSave"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>
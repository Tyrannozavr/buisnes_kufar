<script setup lang="ts">
import type { AnnouncementFormData } from '~/types/announcement';

const router = useRouter();
const saving = ref(false);
const formTouched = ref(false);

const form = ref<AnnouncementFormData>({
  title: '',
  content: '',
  images: []
});

// Store object URLs to revoke them later
const objectUrls = ref<string[]>([]);

// Clean up object URLs when component is unmounted
onBeforeUnmount(() => {
  objectUrls.value.forEach(url => URL.revokeObjectURL(url));
});

const titleError = ref('');
const contentError = ref('');
const imagesError = ref('');

// Computed property to show validation summary
computed(() => {
  if (!formTouched.value) return [];

  const errors = [];
  if (titleError.value) errors.push(titleError.value);
  if (contentError.value) errors.push(contentError.value);
  if (imagesError.value) errors.push(imagesError.value);

  if (!form.value.title) errors.push('Заголовок обязателен');
  else if (form.value.title.length < 5) errors.push('Заголовок должен содержать не менее 5 символов');

  if (!form.value.content) errors.push('Содержание объявления обязательно');
  else if (form.value.content.length < 20) errors.push('Содержание должно содержать не менее 20 символов');

  return errors;
});
const handleSave = async (publish = false) => {
  formTouched.value = true;
  saving.value = true;
  try {
    await useApi('/announcements', {
      method: 'POST',
      body: {
        ...form.value,
        published: publish
      }
    });

    useToast().add({
      title: 'Успешно',
      description: publish ? 'Объявление создано и опубликовано' : 'Объявление сохранено как черновик',
      color: 'success'
    });

    // Redirect back to announcements list
    router.push('/profile');
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
  router.push('/profile');
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

    <AnnouncementForm
      :loading="saving"
      :is-edit="false"
      @save="handleSave"
      @cancel="handleCancel"
    />
  </div>
</template>
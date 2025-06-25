<script setup lang="ts">
import type { AnnouncementFormData } from '~/types/announcement';
import type { AnnouncementCategory } from '~/types/announcement';
import { useAnnouncementsApi } from '~/api/me/announcements'
import PageLoader from "~/components/ui/PageLoader.vue";

const router = useRouter();
const saving = ref(false);
const formTouched = ref(false);

const form = ref<AnnouncementFormData>({
  title: '',
  content: '',
  images: [],
  image_urls: [],
  category: ''
});

const { getAnnouncementCategories, createAnnouncement, uploadAnnouncementImages } = useAnnouncementsApi()

// Fetch categories from API
const { data: categories, error: categoriesError } = await useAsyncData('announcement-categories', () => getAnnouncementCategories())

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
    // Extract images from formData for separate upload
    const { images, ...announcementData } = formData;
    
    // Create announcement first
    const createdAnnouncement = await createAnnouncement({
      ...announcementData,
      images: [], // Empty array for new announcement
      published: publish, // Set published status based on button clicked
      notifications: {
        partners: true,
        customers: true,
        suppliers: true
      }
    });

    // If there are new images to upload, upload them
    if (images && images.length > 0) {
      try {
        // Convert base64 data URLs to File objects
        const files: File[] = [];
        for (const imageData of images) {
          try {
            // Convert base64 to blob
            const response = await fetch(imageData);
            const blob = await response.blob();
            
            // Create file from blob
            const file = new File([blob], `image-${Date.now()}.jpg`, { type: blob.type });
            files.push(file);
          } catch (convertError) {
            console.error('Error converting image:', convertError);
            continue; // Skip this image and continue with others
          }
        }
        
        if (files.length > 0) {
          // Upload images
          await uploadAnnouncementImages(createdAnnouncement.id, files);
        }
      } catch (imageError) {
        console.error('Error uploading images:', imageError);
        useToast().add({
          title: 'Предупреждение',
          description: 'Объявление создано, но не удалось загрузить изображения',
          color: 'warning'
        });
      }
    }

    useToast().add({
      title: 'Успешно',
      description: publish ? 'Объявление создано и опубликовано' : 'Объявление сохранено как черновик',
      color: 'success'
    });

    // Redirect back to announcements list
    router.push('/profile/announcements');
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
  router.push('/profile/announcements');
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <UBreadcrumb
      :items="[
        { label: 'Профиль', to: '/profile' },
        { label: 'Объявления', to: '/profile/announcements' },
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
<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Announcement, AnnouncementFormData } from '~/types/announcement';
import type { AnnouncementCategory } from '~/types/announcement';
import { useAnnouncementsApi } from '~/api/me/announcements'

const route = useRoute();
const router = useRouter();
const id = parseInt(route.params.id as string);

const saving = ref(false);
const { getAnnouncementById, updateAnnouncement, getAnnouncementCategories, uploadAnnouncementImages } = useAnnouncementsApi()

// Fetch announcement data
const { data: announcement, error: fetchError, pending: loading } = await useAsyncData(`announcement-${id}`, () => getAnnouncementById(id));

// Check if announcement exists
const canEdit = computed(() => {
  return announcement.value !== null;
});

// Initial form data
const initialFormData = computed<AnnouncementFormData>(() => {
  if (!announcement.value) {
    return {
      title: '',
      content: '',
      images: [],
      image_urls: [],
      category: '',
      published: false
    };
  }

  return {
    title: announcement.value.title,
    content: announcement.value.content,
    images: [], // New images will be uploaded separately
    image_urls: announcement.value.image_urls || [],
    category: announcement.value.category,
    published: announcement.value.published || false
  };
});

// Fetch categories from API
const { data: categories, error: categoriesError } = await useAsyncData('announcement-categories', () => getAnnouncementCategories())

const handleSave = async (formData: AnnouncementFormData, publish = false) => {
  saving.value = true;
  try {
    // Extract images from formData for separate upload
    const { images, ...announcementData } = formData;
    
    // Update announcement first
    const updatedAnnouncement = await updateAnnouncement(id, {
      ...announcementData,
      images: [], // Keep existing images, new ones will be uploaded separately
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
          await uploadAnnouncementImages(id, files);
        }
      } catch (imageError) {
        console.error('Error uploading images:', imageError);
        useToast().add({
          title: 'Предупреждение',
          description: 'Объявление обновлено, но не удалось загрузить новые изображения',
          color: 'warning'
        });
      }
    }

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
        description="Объявление не найдено"
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
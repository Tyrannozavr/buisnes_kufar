<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue';
import type { AnnouncementFormData } from '~/types/announcement';

const router = useRouter();
const saving = ref(false);

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

const validateTitle = () => {
  if (!form.value.title) {
    titleError.value = 'Заголовок обязателен';
    return false;
  }
  if (form.value.title.length < 5) {
    titleError.value = 'Заголовок должен содержать не менее 5 символов';
    return false;
  }
  titleError.value = '';
  return true;
};

const validateContent = () => {
  if (!form.value.content) {
    contentError.value = 'Содержание объявления обязательно';
    return false;
  }
  if (form.value.content.length < 20) {
    contentError.value = 'Содержание должно содержать не менее 20 символов';
    return false;
  }
  contentError.value = '';
  return true;
};

const isFormValid = () => {
  return validateTitle() && validateContent();
};

const handleSave = async (publish = false) => {
  if (!isFormValid()) {
    return;
  }

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

// Improved file upload handler
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target || !target.files || target.files.length === 0) return;

  // In a real application, you would upload these files to your server
  // and get back URLs to store in the form.images array
  const files = Array.from(target.files);

  // Process each file
  files.forEach(file => {
    // Create a FileReader to read the file as a data URL
    const reader = new FileReader();

    reader.onload = (e) => {
      if (e.target?.result) {
        // Add the data URL to the images array
        form.value.images.push(e.target.result.toString());
      }
    };

    // Read the file as a data URL (base64 encoded string)
    reader.readAsDataURL(file);
  });

  // Reset the input so the same file can be selected again
  target.value = '';
};

const removeImage = (index: number) => {
  form.value.images = form.value.images.filter((_, i) => i !== index);
};
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <UCard class="shadow-lg">
      <template #header>
        <div class="flex items-center justify-between bg-gray-50 p-4 rounded-t-lg">
          <h1 class="text-2xl font-bold text-gray-800">Создание объявления</h1>
          <div class="flex gap-2">
            <UButton
              color="neutral"
              variant="outline"
              to="/profile"
              class="hover:bg-gray-100"
            >
              Отмена
            </UButton>
          </div>
        </div>
      </template>

      <div class="space-y-6 p-4 flex flex-col gap-2">
        <UFormGroup label="Заголовок объявления" required :error="titleError" class="font-medium">
          <UInput
            v-model="form.title"
            placeholder="Введите заголовок объявления"
            :color="titleError ? 'error' : undefined"
            class="focus:ring-2 focus:ring-primary-500 min-w-1/2"
            @blur="validateTitle"
          />
        </UFormGroup>

        <UFormGroup label="Содержание объявления" required :error="contentError" class="font-medium">
          <UTextarea
            v-model="form.content"
            placeholder="Опишите ваше объявление подробно"
            :rows="8"
            :color="contentError ? 'error' : undefined"
            class="focus:ring-2 focus:ring-primary-500 min-w-1/2"
            @blur="validateContent"
          />
        </UFormGroup>

        <UFormGroup label="Изображения" class="font-medium">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div
              v-for="(image, index) in form.images"
              :key="index"
              class="relative aspect-square rounded-lg border overflow-hidden group shadow-sm hover:shadow-md transition-shadow"
            >
              <img :src="image" class="w-full h-full object-cover" />
              <div class="absolute inset-0 bg-transparent group-hover:bg-black/30 transition-all flex items-center justify-center">
                <UButton
                  color="error"
                  variant="solid"
                  size="xs"
                  icon="i-heroicons-trash"
                  class="opacity-0 group-hover:opacity-100 transform transition-all"
                  @click="removeImage(index)"
                />
              </div>
            </div>

            <div
              v-if="form.images.length < 10"
              class="aspect-square rounded-md border-2 border-dashed border-gray-300 flex items-center justify-center
              cursor-pointer hover:bg-gray-50 transition-colors"
            >
              <label for="file-upload" class="w-full h-full flex items-center justify-center cursor-pointer">
                <div class="text-center">
                  <UIcon name="i-heroicons-plus" class="h-8 w-8 text-gray-400 mx-auto" />
                  <p class="text-sm text-gray-500 mt-1">Добавить фото</p>
                </div>
                <input
                  id="file-upload"
                  type="file"
                  accept="image/*"
                  multiple
                  class="hidden"
                  @change="handleImageUpload"
                />
              </label>
            </div>
          </div>
          <p class="text-xs text-gray-500 italic">Вы можете загрузить до 10 изображений</p>
        </UFormGroup>
      </div>

      <template #footer>
        <div class="flex justify-end items-center gap-4 bg-gray-50 p-4 rounded-b-lg">
          <UButton
            color="neutral"
            variant="outline"
            :loading="saving"
            class="px-6 hover:bg-gray-100"
            @click="handleSave(false)"
          >
            Сохранить как черновик
          </UButton>
          <UButton
            color="primary"
            :loading="saving"
            class="px-6 hover:bg-primary-600"
            @click="handleSave(true)"
          >
            Опубликовать
          </UButton>
        </div>
      </template>
    </UCard>
  </div>
</template>
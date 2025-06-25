<script setup lang="ts">
import { ref, onBeforeUnmount, computed, watch } from 'vue';
import type { AnnouncementFormData, AnnouncementCategory } from '~/types/announcement';
import PublishConfirmModal from '~/components/announcement/PublishConfirmModal.vue';

const props = defineProps({
  initialData: {
    type: Object as () => AnnouncementFormData,
    default: () => ({
      title: '',
      content: '',
      images: [],
      image_urls: [],
      category: '',
      published: false
    })
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  categories: {
    type: Array as () => AnnouncementCategory[],
    default: () => []
  }
});

const emit = defineEmits(['save', 'cancel']);

const saving = computed(() => props.loading);
const formTouched = ref(false);
const attemptedSubmit = ref(false);
const showPublishConfirm = ref(false);

const form = ref<AnnouncementFormData>({
  ...props.initialData,
  published: props.initialData.published || false
});

// Notification options
const notifyOptions = ref({
  notify: false,
  partners: false,
  customers: false,
  suppliers: false
});

// Track which fields have been touched
const touchedFields = ref({
  title: false,
  content: false,
  images: false,
  category: false
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

// Validate title with detailed feedback
const validateTitle = () => {
  touchedFields.value.title = true;
  formTouched.value = true;

  if (!form.value.title) {
    titleError.value = 'Заголовок обязателен';
    return false;
  }
  if (form.value.title.length < 5) {
    titleError.value = 'Заголовок должен содержать не менее 5 символов';
    return false;
  }
  if (form.value.title.length > 100) {
    titleError.value = 'Заголовок не должен превышать 100 символов';
    return false;
  }
  titleError.value = '';
  return true;
};

// Validate content with detailed feedback
const validateContent = () => {
  touchedFields.value.content = true;
  formTouched.value = true;

  if (!form.value.content) {
    contentError.value = 'Содержание объявления обязательно';
    return false;
  }
  if (form.value.content.length < 20) {
    contentError.value = 'Содержание должно содержать не менее 20 символов';
    return false;
  }
  if (form.value.content.length > 5000) {
    contentError.value = 'Содержание не должно превышать 5000 символов';
    return false;
  }
  contentError.value = '';
  return true;
};

// Validate images
const validateImages = () => {
  touchedFields.value.images = true;

  const totalImages = form.value.images.length + form.value.image_urls.length;
  if (totalImages > 10) {
    imagesError.value = 'Максимальное количество изображений - 10';
    return false;
  }
  imagesError.value = '';
  return true;
};


// Watch for changes to validate in real-time after first interaction
watch(() => form.value.title, () => {
  if (touchedFields.value.title) validateTitle();
});

watch(() => form.value.content, () => {
  if (touchedFields.value.content) validateContent();
});

watch([() => form.value.images, () => form.value.image_urls], () => {
  if (touchedFields.value.images) validateImages();
}, { deep: true });


// Reset notification options when main notify checkbox is unchecked
watch(() => notifyOptions.value.notify, (newValue) => {
  if (!newValue) {
    notifyOptions.value.partners = false;
    notifyOptions.value.customers = false;
    notifyOptions.value.suppliers = false;
  }
});

// Computed property to check if form is valid
const isFormValid = computed(() => {
  return !titleError.value && !contentError.value && !imagesError.value &&
         form.value.title.length >= 5 && form.value.content.length >= 20;
});

// Computed property to show validation summary
const validationSummary = computed(() => {
  if (!attemptedSubmit.value) return [];

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

const confirmPublish = () => {
  showPublishConfirm.value = true;
};

const closePublishModal = () => {
  showPublishConfirm.value = false;
};

const handlePublishConfirm = () => {
  handleSave(true);
};

const handleSave = async (publish = false) => {
  attemptedSubmit.value = true;
  formTouched.value = true;

  // Mark all fields as touched
  touchedFields.value = {
    title: true,
    content: true,
    images: true,
    category: true
  };

  // Validate all fields
  const titleValid = validateTitle();
  const contentValid = validateContent();
  const imagesValid = validateImages();

  if (!titleValid || !contentValid || !imagesValid) {
    useToast().add({
      title: 'Ошибка валидации',
      description: 'Пожалуйста, исправьте ошибки в форме',
      color: 'warning'
    });
    return;
  }

  // Include notification options in the form data
  const formData = {
    ...form.value,
    notifications: notifyOptions.value.notify ? {
      partners: notifyOptions.value.partners,
      customers: notifyOptions.value.customers,
      suppliers: notifyOptions.value.suppliers
    } : null
  };
  // дату объявления сохранять на момент публикации, а не редактирования
  // уведомления приходят один раз
  emit('save', formData, publish);

  // Close modal if it was open
  showPublishConfirm.value = false;
};

// Improved file upload handler
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target || !target.files || target.files.length === 0) return;

  touchedFields.value.images = true;

  // Check if adding these files would exceed the limit
  const totalImages = form.value.images.length + form.value.image_urls.length;
  if (totalImages + target.files.length > 10) {
    imagesError.value = 'Максимальное количество изображений - 10';
    useToast().add({
      title: 'Превышен лимит',
      description: 'Вы можете загрузить максимум 10 изображений',
      color: 'warning'
    });
    target.value = '';
    return;
  }

  // In a real application, you would upload these files to your server
  // and get back URLs to store in the form.images array
  const files = Array.from(target.files);

  // Process each file
  files.forEach(file => {
    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      useToast().add({
        title: 'Файл слишком большой',
        description: `${file.name} превышает максимальный размер 5MB`,
        color: 'warning'
      });
      return;
    }

    // Create a FileReader to read the file as a data URL
    const reader = new FileReader();

    reader.onload = (e) => {
      if (e.target?.result) {
        // Add the data URL to the images array (new uploaded files)
        form.value.images.push(e.target.result.toString());
      }
    };

    // Read the file as a data URL (base64 encoded string)
    reader.readAsDataURL(file);
  });

  // Reset the input so the same file can be selected again
  target.value = '';
};

const removeImage = (index: number, isExistingImage: boolean = false) => {
  touchedFields.value.images = true;
  
  if (isExistingImage) {
    // Remove from existing image_urls
    form.value.image_urls = form.value.image_urls.filter((_, i) => i !== index);
  } else {
    // Remove from new uploaded images
    form.value.images = form.value.images.filter((_, i) => i !== index);
  }
};
</script>

<template>
  <UCard class="shadow-lg">
    <template #header>
      <div class="flex items-center justify-between bg-gray-50 p-4 rounded-t-lg">
        <h1 class="text-2xl font-bold text-gray-800">
          {{ isEdit ? 'Редактирование объявления' : 'Создание объявления' }}
        </h1>
        <div class="flex gap-2">
          <UButton
            color="neutral"
            variant="outline"
            class="hover:bg-gray-100"
            @click="$emit('cancel')"
          >
            Отмена
          </UButton>
        </div>
      </div>
    </template>

    <div class="space-y-6 p-4 flex flex-col gap-2">
      <!-- Form validation summary - only show after attempted submit -->
      <UAlert
        v-if="attemptedSubmit && validationSummary.length > 0"
        color="warning"
        title="Пожалуйста, исправьте следующие ошибки:"
        icon="i-heroicons-exclamation-triangle"
        class="mb-4"
      >
        <ul class="list-disc pl-5 mt-2">
          <li v-for="(error, index) in validationSummary" :key="index" class="text-sm">
            {{ error }}
          </li>
        </ul>
      </UAlert>

      <UFormField label="Заголовок объявления" required :error="touchedFields.title ? titleError : ''" class="font-medium">
        <UInput
          v-model="form.title"
          placeholder="Введите заголовок объявления"
          :color="touchedFields.title && titleError ? 'error' : undefined"
          class="focus:ring-2 focus:ring-primary-500 min-w-1/2"
          @blur="validateTitle"
        />
        <template #hint>
          <div class="flex justify-between gap-0.5">
            <span>Минимум 5 символов</span>
            <span :class="{ 'text-red-500': form.title.length > 100 }">
              {{ form.title.length }}/100
            </span>
          </div>
        </template>
      </UFormField>

      <UFormField label="Содержание объявления" required :error="touchedFields.content ? contentError : ''" class="font-medium">
        <UTextarea
          v-model="form.content"
          placeholder="Опишите ваше объявление подробно"
          :rows="8"
          :color="touchedFields.content && contentError ? 'error' : undefined"
          class="focus:ring-2 focus:ring-primary-500 min-w-1/2"
          @blur="validateContent"
        />
        <template #hint>
          <div class="flex justify-between gap-0.5">
            <span>Минимум 20 символов</span>
            <span :class="{ 'text-red-500': form.content.length > 5000 }">
              {{ form.content.length }}/5000
            </span>
          </div>
        </template>
      </UFormField>
      <UFormField label="Изображения" class="font-medium" :error="touchedFields.images ? imagesError : ''">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <!-- Existing images (image_urls) -->
          <div
            v-for="(image, index) in form.image_urls"
            :key="`existing-${index}`"
            class="relative aspect-square rounded-lg border overflow-hidden group shadow-sm hover:shadow-md transition-shadow"
          >
            <NuxtImg :src="image" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-transparent group-hover:bg-black/30 transition-all flex items-center justify-center">
              <UButton
                color="error"
                variant="solid"
                size="xs"
                icon="i-heroicons-trash"
                class="opacity-0 group-hover:opacity-100 transform transition-all"
                @click="removeImage(index, true)"
              />
            </div>
          </div>

          <!-- New uploaded images (images) -->
          <div
            v-for="(image, index) in form.images"
            :key="`new-${index}`"
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
                @click="removeImage(index, false)"
              />
            </div>
          </div>

          <!-- Add new image button -->
          <div
            v-if="(form.images.length + form.image_urls.length) < 10"
            class="aspect-square rounded-md border-2 border-dashed border-gray-300 flex items-center justify-center
            cursor-pointer hover:bg-gray-50 transition-colors"
          >
            <label for="file-upload" class="w-full h-full flex items-center justify-center cursor-pointer">
              <div class="text-center">
                <UIcon name="i-heroicons-plus" class="h-8 w-8 text-gray-400 mx-auto" />
                <p class="mt-1 text-sm text-gray-500">Добавить изображение</p>
              </div>
            </label>
            <input id="file-upload" type="file" accept="image/*" multiple @change="handleImageUpload" class="hidden" />
          </div>
        </div>
        
        <!-- Image count hint -->
        <template #hint>
          <div class="flex justify-between text-sm text-gray-500">
            <span>Максимум 10 изображений</span>
            <span>{{ form.images.length + form.image_urls.length }}/10</span>
          </div>
        </template>
      </UFormField>
      <!-- Category selection -->
      <UFormField label="Категория">
        <select
            v-model="form.category"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="">Выберите категорию</option>
          <option 
            v-for="category in categories" 
            :key="category.name"
            :value="category.name"
          >
            {{ category.name }}
          </option>
        </select>
        <template #hint v-if="form.category">
          <span>{{ categories.find(c => c.id === form.category)?.description || '' }}</span>
        </template>
      </UFormField>
      <!-- Notification options -->
      <UFormField label="Настройки уведомлений" class="font-medium">
        <div class="space-y-3 mt-2">
          <UCheckbox
            v-model="notifyOptions.notify"
            label="Оповестить об объявлении"
            :disabled="isEdit"
            class="font-normal"
          />

          <div class="ml-6 space-y-2">
            <UCheckbox
              v-model="notifyOptions.partners"
              label="Партнеры"
              :disabled="!notifyOptions.notify"
              class="font-normal"
            />
            <UCheckbox
              v-model="notifyOptions.customers"
              label="Покупатели"
              :disabled="!notifyOptions.notify"
              class="font-normal"
            />
            <UCheckbox
              v-model="notifyOptions.suppliers"
              label="Поставщики"
              :disabled="!notifyOptions.notify"
              class="font-normal"
            />
          </div>
        </div>
      </UFormField>

    </div>

    <div class="flex justify-end p-4 bg-gray-50 rounded-b-lg">
      <UButton
        color="primary"
        :disabled="!isFormValid || saving"
        class="mr-2 cursor-pointer"
        @click="() => handleSave(false)"
      >
        Сохранить черновик
      </UButton>
      <UButton
        color="success"
        :disabled="!isFormValid || saving"
        class="cursor-pointer"
        :loading="saving"
        @click="confirmPublish"
      >
        Опубликовать
      </UButton>
    </div>
  </UCard>

  <!-- Используем новый компонент для модального окна -->
  <PublishConfirmModal
    :open="showPublishConfirm"
    :saving="loading"
    :notify-options="notifyOptions"
    @close="closePublishModal"
    @confirm="handlePublishConfirm"
  />
</template>
<script setup>
const props = defineProps({
  product: {
    type: Object,
    default: null
  },
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['save', 'update:modelValue']);

// Form data with default values
const formData = ref({
  type: 'Товар',
  name: '',
  price: '',
  unitCategory: 'economic',
  unit: 'шт',
  characteristics: [],
  images: []
});
const productTypeItems = ['Товар', 'Услуга'];
// Units mapping based on category
const unititems = {
  economic: [
    { value: 'шт', label: 'Штука' },
    { value: 'упак', label: 'Упаковка' },
    { value: 'компл', label: 'Комплект' }
  ],
  length: [
    { value: 'мм', label: 'Миллиметр' },
    { value: 'см', label: 'Сантиметр' },
    { value: 'м', label: 'Метр' }
  ],
  area: [
    { value: 'м²', label: 'Квадратный метр' },
    { value: 'га', label: 'Гектар' }
  ],
  volume: [
    { value: 'мл', label: 'Миллилитр' },
    { value: 'л', label: 'Литр' },
    { value: 'м³', label: 'Кубический метр' }
  ],
  mass: [
    { value: 'г', label: 'Грамм' },
    { value: 'кг', label: 'Килограмм' },
    { value: 'т', label: 'Тонна' }
  ]
};

// Computed property to get available units based on selected category
const availableUnits = computed(() => {
  return unititems[formData.value.unitCategory] || [];
});

// Initialize form data when product prop changes
watch(() => props.product, (newProduct) => {
  if (newProduct) {
    formData.value = {
      type: newProduct.type || 'Товар',
      name: newProduct.name || '',
      price: newProduct.price || '',
      unitCategory: newProduct.unitCategory || 'economic',
      unit: newProduct.unit || 'шт',
      characteristics: [...(newProduct.characteristics || [])],
      images: [...(newProduct.images || [])]
    };
  } else {
    // Reset form for new product
    formData.value = {
      type: 'Товар',
      name: '',
      price: '',
      unitCategory: 'economic',
      unit: 'шт',
      characteristics: [],
      images: []
    };
  }
}, { immediate: true });

// Add a new characteristic field
const addCharacteristic = () => {
  formData.value.characteristics.push({ name: '', value: '' });
};

// Remove a characteristic field
const removeCharacteristic = (index) => {
  formData.value.characteristics.splice(index, 1);
};

// Handle image upload
const handleImageUpload = (event) => {
  const files = event.target.files;
  if (!files || files.length === 0) return;

  for (const file of files) {
    const reader = new FileReader();
    reader.onload = (e) => {
      formData.value.images.push(e.target.result);
    };
    reader.readAsDataURL(file);
  }
};

// Remove an image
const removeImage = (index) => {
  formData.value.images.splice(index, 1);
};

// Submit form
const handleSubmit = () => {
  emit('save', { ...formData.value });
};

// Reference to the file input element
const fileInputRef = ref(null);

// Trigger file input click
const triggerFileInput = () => {
  if (fileInputRef.value) {
    fileInputRef.value.click();
  }
};

// Update the close handler
const handleClose = () => {
  emit('update:modelValue', false);
};
</script>


<template>
  <UModal :open="modelValue" @update:open="emit('update:modelValue', $event)" :ui="{ width: 'max-w-3xl' }">
    <template #header>
      <div class="flex justify-between items-center">
        <h3 class="text-xl font-semibold">
          {{ product ? 'Редактировать продукт' : 'Добавить продукт' }}
        </h3>
        <UButton
          color="neutral"
          variant="ghost"
          icon="i-heroicons-x-mark"
          @click="handleClose"
        />
      </div>
    </template>
    <template #body>
      <div class="p-4">
        <form class="space-y-6" @submit.prevent="handleSubmit">
          <URadioGroup
              v-model="formData.type"
              orientation="horizontal"
              label="Тип продукта"
              :items="productTypeItems"
          />

          <UFormField label="Наименование" required>
            <UInput
              v-model="formData.name"
              placeholder="Введите наименование продукта"
            />
          </UFormField>

          <UFormField label="Цена">
            <UInput
              v-model="formData.price"
              type="number"
              min="0"
              step="0.01"
              placeholder="Введите цену"
            />
          </UFormField>

          <UFormField label="Единица измерения">
            <div class="grid grid-cols-2 gap-4">
              <USelect
                v-model="formData.unitCategory"
                :items="[
                  { label: 'Экономические единицы', value: 'economic' },
                  { label: 'Единицы длины', value: 'length' },
                  { label: 'Единицы площади', value: 'area' },
                  { label: 'Единицы объема', value: 'volume' },
                  { label: 'Единицы массы', value: 'mass' }
                ]"
                placeholder="Выберите категорию"
              />
              <USelect
                v-model="formData.unit"
                :items="availableUnits"
                placeholder="Выберите единицу"
              />
            </div>
          </UFormField>

          <div class="space-y-4">
            <div class="flex justify-between items-center">
              <h4 class="font-medium text-lg">Характеристики</h4>
              <UButton
                type="button"
                color="primary"
                variant="soft"
                size="sm"
                icon="i-heroicons-plus"
                @click="addCharacteristic"
              >
                Добавить характеристику
              </UButton>
            </div>

            <div v-for="(char, index) in formData.characteristics" :key="index" class="grid grid-cols-5 gap-4 items-center">
              <UInput
                v-model="char.name"
                placeholder="Название характеристики"
                class="col-span-2"
              />
              <UInput
                v-model="char.value"
                placeholder="Значение характеристики"
                class="col-span-2"
              />
              <UButton
                type="button"
                color="error"
                variant="soft"
                icon="i-heroicons-trash"
                @click="removeCharacteristic(index)"
              />
            </div>
          </div>

          <UFormField label="Изображения">
            <div class="space-y-4">
              <!-- Hidden file input -->
              <input
                ref="fileInputRef"
                type="file"
                multiple
                accept="image/*"
                @change="handleImageUpload"
                class="hidden"
              />

              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <!-- Existing images -->
                <div
                  v-for="(image, index) in formData.images"
                  :key="index"
                  class="relative aspect-square rounded-lg border overflow-hidden group"
                >
                  <img :src="image" :alt="'Preview ' + (index + 1)" class="w-full h-full object-cover">
                  <div class="absolute inset-0 bg-transparent group-hover:bg-black/30 transition-all flex items-center justify-center">
                    <UButton
                      type="button"
                      color="error"
                      variant="solid"
                      size="xs"
                      icon="i-heroicons-trash"
                      class="opacity-0 group-hover:opacity-100 transform transition-all"
                      @click="removeImage(index)"
                    />
                  </div>
                </div>

                <!-- Add image button styled like an image -->
                <div
                  class="aspect-square rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center
                  cursor-pointer hover:bg-gray-50 transition-colors"
                  @click="triggerFileInput"
                >
                  <div class="text-center">
                    <UIcon name="i-heroicons-plus" class="h-8 w-8 text-gray-400 mx-auto" />
                    <p class="mt-1 text-sm text-gray-500">Добавить</p>
                  </div>
                </div>
              </div>
            </div>
          </UFormField>
        </form>
      </div>
    </template>
    <template #footer>
      <div class="flex justify-end gap-3">
        <UButton
          color="neutral"
          variant="outline"
          @click="handleClose"
        >
          Отмена
        </UButton>
        <UButton
          color="primary"
          @click="handleSubmit"
        >
          {{ product ? 'Сохранить изменения' : 'Добавить продукт' }}
        </UButton>
      </div>
    </template>
  </UModal>
</template>


<style scoped>
/* We can remove most of these styles as they're now handled by Nuxt UI components */
.product-form-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}
</style>
<script setup lang="ts">
import type { Product } from '~/types/product'
import { uploadProductImages, deleteProductImage, createProductWithImages } from '~/api/me/products'

const props = defineProps({
  product: {
    type: Object as PropType<Product | null>,
    default: null
  },
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['save', 'update:modelValue', 'done']);

// Form data with default values
const formData = ref({
  type: 'Товар' as 'Товар' | 'Услуга',
  article: '',
  name: '',
  description: '',
  price: 0 as number,
  unitCategory: 'economic' as string,
  unit_of_measurement: 'шт',
  characteristics: [] as Array<{ name: string; value: string }>,
  images: [] as string[],
  selectedFiles: [] as File[]
});

const loading = ref(false);
const productTypeItems = ['Товар', 'Услуга'];

// Units mapping based on category
const unititems: Record<string, Array<{ value: string; label: string }>> = {
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

const unitCategoryNameByItem = (unitName: string) => {
  let category = formData.value.unitCategory;
  for (const [key, units] of Object.entries(unititems)) {
    if (units.some(unit => unit.value === unitName)) {
      category = key;
      break;
    }
  }
  return category;
}

// Computed property to get available units based on selected category
const availableUnits = computed(() => {
  return unititems[formData.value.unitCategory] || [];
});

// Initialize form data when product prop changes
watch(() => props.product, (newProduct) => {
  if (newProduct) {
    formData.value = {
      type: newProduct.type || 'Товар',
      article: newProduct.article || '',
      name: newProduct.name || '',
      description: newProduct.description || '',
      price: newProduct.price || 0,
      unit_of_measurement: newProduct.unit_of_measurement || 'шт',
      unitCategory: unitCategoryNameByItem(newProduct.unit_of_measurement || ''),
      characteristics: [...(newProduct.characteristics || [])],
      images: [...(newProduct.images || [])],
      selectedFiles: []
    };
  } else {
    // Reset form for new product
    formData.value = {
      type: 'Товар',
      article: '',
      name: '',
      description: '',
      price: 0,
      unitCategory: 'economic',
      unit_of_measurement: 'шт',
      characteristics: [],
      images: [],
      selectedFiles: []
    };
  }
}, { immediate: true });

// Add a new characteristic field
const addCharacteristic = () => {
  formData.value.characteristics.push({ name: '', value: '' });
};

// Remove a characteristic field
const removeCharacteristic = (index: number) => {
  formData.value.characteristics.splice(index, 1);
};

// Handle image upload for new products
const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = target.files;
  if (!files || files.length === 0) return;

  if (props.product?.id) {
    // Для существующих продуктов - загружаем через API
    loading.value = true;
    try {
      const fileArray = Array.from(files) as File[];
      const response = await uploadProductImages(props.product.id, fileArray);
      
      if (response) {
        formData.value.images = response.images;
        useToast().add({
          title: 'Успешно',
          description: 'Изображения загружены',
          color: 'success'
        });
      }
    } catch (error) {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось загрузить изображения',
        color: 'error'
      });
    } finally {
      loading.value = false;
    }
  } else {
    // Для новых продуктов - добавляем в локальный массив
    const fileArray = Array.from(files) as File[];
    formData.value.selectedFiles.push(...fileArray);
    
    // Создаем превью для отображения
    for (const file of fileArray) {
      const reader = new FileReader();
      reader.onload = (e) => {
        formData.value.images.push(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  }
};

// Remove an image
const removeImage = async (index: number) => {
  if (props.product?.id) {
    // Для существующих продуктов - удаляем через API
    loading.value = true;
    try {
      const response = await deleteProductImage(props.product.id, index);
      
      if (response) {
        formData.value.images = response.images;
        useToast().add({
          title: 'Успешно',
          description: 'Изображение удалено',
          color: 'success'
        });
      }
    } catch (error) {
      useToast().add({
        title: 'Ошибка',
        description: 'Не удалось удалить изображение',
        color: 'error'
      });
    } finally {
      loading.value = false;
    }
  } else {
    // Для новых продуктов - удаляем из локальных массивов
    formData.value.images.splice(index, 1);
    formData.value.selectedFiles.splice(index, 1);
  }
};

// Submit form
const handleSubmit = () => {
  // Убираем images и selectedFiles из данных формы
  const { images, selectedFiles, ...submitData } = formData.value;
  
  if (props.product?.id) {
    // Для существующих продуктов - отправляем только данные
    emit('save', submitData);
  } else {
    // Для новых продуктов - отправляем данные с файлами
    emit('save', { ...submitData, files: selectedFiles });
  }
};

// Handle done button for new products
const handleDone = () => {
  emit('done');
  emit('update:modelValue', false);
};

// Reference to the file input element
const fileInputRef = ref<HTMLInputElement | null>(null);

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
  <UModal :open="modelValue" @update:open="emit('update:modelValue', $event)">
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
          <!-- Изображения (для всех продуктов) -->
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
                        :loading="loading"
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

          <URadioGroup
              v-model="formData.type"
              orientation="horizontal"
              label="Тип продукта"
              :items="productTypeItems"
          />
          <UFormField label="Артикул" required>
            <UInput
              v-model="formData.article"
              placeholder="Введите артикул продукта"
              class="min-w-full"

            />
          </UFormField>

          <UFormField label="Наименование" required>
            <UInput
              v-model="formData.name"
              placeholder="Введите наименование продукта"
              class="min-w-full"

            />
          </UFormField>

          <UFormField label="Описание">
            <UTextarea
              v-model="formData.description"
              placeholder="Введите описание продукта"
              class="min-w-full"
              :rows="4"
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
                v-model="formData.unit_of_measurement"
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
        
        <!-- Show "Done" button for new products that have been created -->
        <UButton
          v-if="product?.id && (!product.images || product.images.length === 0)"
          color="success"
          @click="handleDone"
        >
          Готово
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
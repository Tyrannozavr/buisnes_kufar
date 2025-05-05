<template>
  <div class="product-form-modal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ product ? 'Редактировать продукт' : 'Добавить продукт' }}</h2>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <form @submit.prevent="handleSubmit" class="form">
        <div class="form-group">
          <label for="type">Тип продукта *</label>
          <select id="type" v-model="formData.type" required>
            <option value="Товар">Товар</option>
            <option value="Услуга">Услуга</option>
          </select>
        </div>

        <div class="form-group">
          <label for="name">Наименование *</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="Введите наименование продукта"
          >
        </div>

        <div class="form-group">
          <label for="price">Цена</label>
          <input
            id="price"
            v-model="formData.price"
            type="number"
            min="0"
            step="0.01"
            placeholder="Введите цену"
          >
        </div>

        <div class="form-group">
          <label>Единица измерения</label>
          <div class="unit-selectors">
            <select v-model="formData.unitCategory">
              <option value="economic">Экономические единицы</option>
              <option value="length">Единицы длины</option>
              <option value="area">Единицы площади</option>
              <option value="volume">Единицы объема</option>
              <option value="mass">Единицы массы</option>
            </select>
            <select v-model="formData.unit">
              <option v-for="unit in availableUnits" :key="unit.value" :value="unit.value">
                {{ unit.label }}
              </option>
            </select>
          </div>
        </div>

        <div class="characteristics">
          <h3>Характеристики</h3>
          <div v-for="(char, index) in formData.characteristics" :key="index" class="characteristic">
            <input
              v-model="char.name"
              type="text"
              placeholder="Название характеристики"
            >
            <input
              v-model="char.value"
              type="text"
              placeholder="Значение характеристики"
            >
            <button type="button" class="remove-btn" @click="removeCharacteristic(index)">
              Удалить
            </button>
          </div>
          <button type="button" class="add-btn" @click="addCharacteristic">
            Добавить характеристику
          </button>
        </div>

        <div class="form-group">
          <label>Изображения</label>
          <div class="image-upload">
            <input
              type="file"
              multiple
              accept="image/*"
              @change="handleImageUpload"
            >
            <div class="image-preview" v-if="formData.images.length">
              <div v-for="(image, index) in formData.images" :key="index" class="preview-item">
                <img :src="image" :alt="'Preview ' + (index + 1)">
                <button type="button" class="remove-btn" @click="removeImage(index)">
                  &times;
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="save-btn">
            {{ product ? 'Сохранить изменения' : 'Добавить продукт' }}
          </button>
          <button type="button" class="cancel-btn" @click="$emit('close')">
            Отмена
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Product } from '~/types/product'
import { ref, computed } from 'vue'

const props = defineProps<{
  product: Product | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: Partial<Product>): void
}>()

const formData = ref({
  type: props.product?.type || 'Товар',
  name: props.product?.name || '',
  price: props.product?.price || 0,
  unitCategory: 'economic',
  unit: 'шт',
  characteristics: props.product?.characteristics || [],
  images: props.product?.images || []
})

const units = {
  economic: [
    { value: 'шт', label: 'Штука, шт' },
    { value: 'боб', label: 'Бобина, боб' },
    { value: 'л', label: 'Лист, л.' },
    { value: 'набор', label: 'Набор, набор' },
    { value: 'пар', label: 'Пара, пар' },
    { value: 'рул', label: 'Рулон, рул' }
  ],
  length: [
    { value: 'мм', label: 'Миллиметр, мм' },
    { value: 'см', label: 'Сантиметр, см' },
    { value: 'м', label: 'Метр, м' },
    { value: 'км', label: 'Километр, км' },
    { value: 'пог.м', label: 'Погонный метр, пог. м' }
  ],
  area: [
    { value: 'мм2', label: 'Квадратный миллиметр, мм²' },
    { value: 'см2', label: 'Квадратный сантиметр, см²' },
    { value: 'м2', label: 'Квадратный метр, м²' },
    { value: 'км2', label: 'Квадратный километр, км²' },
    { value: 'га', label: 'Гектар, га' }
  ],
  volume: [
    { value: 'мл', label: 'Миллилитр, мл' },
    { value: 'л', label: 'Литр, л' },
    { value: 'мм3', label: 'Кубический миллиметр, мм³' },
    { value: 'см3', label: 'Кубический сантиметр, см³' },
    { value: 'м3', label: 'Кубический метр, м³' }
  ],
  mass: [
    { value: 'мг', label: 'Миллиграмм, мг' },
    { value: 'г', label: 'Грамм, г' },
    { value: 'кг', label: 'Килограмм, кг' },
    { value: 'т', label: 'Тонна, т' }
  ]
}

const availableUnits = computed(() => units[formData.value.unitCategory])

const addCharacteristic = () => {
  formData.value.characteristics.push({ name: '', value: '' })
}

const removeCharacteristic = (index: number) => {
  formData.value.characteristics.splice(index, 1)
}

const handleImageUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files) {
    Array.from(input.files).forEach(file => {
      const reader = new FileReader()
      reader.onload = (e) => {
        if (e.target?.result) {
          formData.value.images.push(e.target.result as string)
        }
      }
      reader.readAsDataURL(file)
    })
  }
}

const removeImage = (index: number) => {
  formData.value.images.splice(index, 1)
}

const handleSubmit = () => {
  emit('save', formData.value)
}
</script>

<style scoped>
.product-form-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.form {
  padding: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
}

input[type="text"],
input[type="number"],
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.unit-selectors {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.characteristics {
  margin: 1rem 0;
}

.characteristic {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.image-upload {
  margin-top: 0.5rem;
}

.image-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.preview-item {
  position: relative;
  aspect-ratio: 1;
}

.preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.preview-item .remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
}

.add-btn,
.remove-btn {
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.add-btn {
  background-color: #4CAF50;
  color: white;
  width: 100%;
  margin-top: 0.5rem;
}

.remove-btn {
  background-color: #f44336;
  color: white;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.save-btn,
.cancel-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  flex: 1;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
}

.cancel-btn {
  background-color: #9e9e9e;
  color: white;
}

.save-btn:hover {
  background-color: #45a049;
}

.cancel-btn:hover {
  background-color: #757575;
}
</style> 
<script setup lang="ts">
import { ref, nextTick } from 'vue'

const props = defineProps<{
  quantity: number
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:quantity': [value: number]
  'remove': []
}>()

const isEditing = ref(false)
const inputValue = ref('')

const handleQuantityInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value.replace(/[^\d]/g, '')
  inputValue.value = value
}

const handleQuantityBlur = () => {
  const newQuantity = parseInt(inputValue.value) || 0
  if (newQuantity > 0) {
    emit('update:quantity', newQuantity)
  } else {
    inputValue.value = props.quantity.toString()
  }
  isEditing.value = false
}

const handleQuantityKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    handleQuantityBlur()
  }
}

const startEditing = () => {
  inputValue.value = props.quantity.toString()
  isEditing.value = true
  // Фокусируемся на поле ввода после его появления
  nextTick(() => {
    const input = document.querySelector('.quantity-input') as HTMLInputElement
    if (input) {
      input.focus()
      input.select()
    }
  })
}

const handleDecrease = () => {
  if (props.quantity > 1) {
    emit('update:quantity', props.quantity - 1)
  } else {
    emit('remove')
  }
}

const handleIncrease = () => {
  emit('update:quantity', props.quantity + 1)
}
</script>

<template>
  <div class="flex items-center space-x-2">
    <UButton
      color="neutral"
      variant="soft"
      icon="i-heroicons-minus"
      :disabled="disabled"
      @click="handleDecrease"
    />

    <div
      v-if="!isEditing"
      class="quantity-display"
      title="Нажмите для ввода количества"
      @click="startEditing"
    >
      <span>{{ quantity }}</span>
      <UIcon name="i-heroicons-pencil-square" class="w-3 h-3 ml-1 text-gray-400" />
    </div>
    <input
      v-else
      ref="quantityInput"
      v-model="inputValue"
      type="text"
      class="quantity-input"
      placeholder="Введите количество"
      @input="handleQuantityInput"
      @blur="handleQuantityBlur"
      @keydown="handleQuantityKeydown"
    />

    <UButton
      color="neutral"
      variant="soft"
      icon="i-heroicons-plus"
      :disabled="disabled"
      @click="handleIncrease"
    />
  </div>
</template>

<style scoped>
.quantity-display {
  min-width: 40px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 500;
  color: #2d3748;
  cursor: text;
  padding: 0 0.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  background: white;
  transition: all 0.2s ease;
}

.quantity-display:hover {
  border-color: #4CAF50;
}

.quantity-input {
  width: 80px;
  height: 28px;
  text-align: center;
  border: 1px solid #4CAF50;
  border-radius: 4px;
  font-size: 0.875rem;
  padding: 0 0.5rem;
  outline: none;
  background: white;
}

.quantity-input:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.quantity-input::placeholder {
  color: #a0aec0;
}
</style>
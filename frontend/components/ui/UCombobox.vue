<script setup lang="ts">
import type { LocationItem } from '~/types/location'
import { onClickOutside } from '@vueuse/core'

interface Props {
  modelValue: LocationItem | undefined
  items: LocationItem[]
  loading?: boolean
  disabled?: boolean
  placeholder?: string
  disabledMessage?: string
  searchInput?: {
    modelValue: string
    'onUpdate:modelValue': (value: string) => void
    placeholder?: string
    icon?: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  placeholder: '',
  disabledMessage: '',
  searchInput: undefined
})

const emit = defineEmits<{
  'update:modelValue': [value: LocationItem | undefined]
}>()

const isOpen = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)
const dropdownRef = ref<HTMLDivElement | null>(null)
const isSearching = ref(false)

// Обработка клика вне компонента для закрытия выпадающего списка
onClickOutside(dropdownRef, () => {
  isOpen.value = false
  isSearching.value = false
})

// Обработка выбора элемента
const selectItem = (item: LocationItem) => {
  emit('update:modelValue', item)
  isOpen.value = false
  isSearching.value = false
  if (props.searchInput) {
    props.searchInput['onUpdate:modelValue']('')
  }
}

// Обработка фокуса на инпуте
const handleFocus = () => {
  if (!props.disabled) {
    isOpen.value = true
    isSearching.value = true
  }
}

// Обработка ввода в поле поиска
const handleInput = (event: Event) => {
  if (props.searchInput) {
    const target = event.target as HTMLInputElement
    props.searchInput['onUpdate:modelValue'](target.value)
    isSearching.value = true
  }
}

// Обработка клавиш для навигации
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    isOpen.value = false
    isSearching.value = false
  } else if (event.key === 'Enter' && props.searchInput && props.searchInput.modelValue.trim()) {
    // Создаем новый элемент из введенного текста
    const newItem: LocationItem = {
      value: props.searchInput.modelValue.trim(),
      label: props.searchInput.modelValue.trim()
    }
    selectItem(newItem)
  }
}

// Вычисляемое свойство для отображения значения в инпуте
const displayValue = computed(() => {
  if (isSearching.value && props.searchInput) {
    return props.searchInput.modelValue
  }
  return props.modelValue?.label || ''
})
</script>

<template>
  <div class="relative" ref="dropdownRef">
    <!-- Поле ввода -->
    <div class="relative">
      <input
          ref="inputRef"
          type="text"
          :value="displayValue"
          :placeholder="placeholder"
          :disabled="disabled"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          :class="{
            'border-gray-300': !isOpen,
            'border-primary-500': isOpen,
            'pr-10': true
          }"
          @focus="handleFocus"
          @input="handleInput"
          @keydown="handleKeydown"
      />
      <!-- Иконка поиска или стрелки -->
      <div class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <UIcon
            :name="searchInput?.icon || 'i-heroicons-chevron-down'"
            class="w-5 h-5 text-gray-400"
            :class="{ 'transform rotate-180': isOpen }"
        />
      </div>
    </div>

    <!-- Сообщение о неактивном состоянии -->
    <p v-if="disabled && disabledMessage" class="text-gray-500 text-sm mt-1">
      {{ disabledMessage }}
    </p>

    <!-- Выпадающий список -->
    <div
        v-if="isOpen"
        class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto"
    >
      <!-- Индикатор загрузки -->
      <div v-if="loading" class="p-2 text-center text-gray-500">
        <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin mx-auto" />
        <span class="ml-2">Загрузка...</span>
      </div>

      <!-- Список элементов -->
      <template v-else>
        <div v-if="items.length === 0" class="p-2 text-center text-gray-500">
          Ничего не найдено
        </div>
        <button
            v-for="item in items"
            :key="item.value"
            class="w-full px-3 py-2 text-left hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
            :class="{ 'bg-gray-50': modelValue?.value === item.value }"
            @click="selectItem(item)"
        >
          {{ item.label }}
        </button>
      </template>
    </div>
  </div>
</template>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 
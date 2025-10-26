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
  searchable?: boolean
  onBlur?: () => void
  searchInput?: {
    modelValue: string
    'onUpdate:modelValue': (value: string) => void
    placeholder?: string
    icon?: string
  }
  allowCustomInput?: boolean // Разрешить ввод произвольных значений
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  placeholder: '',
  disabledMessage: '',
  searchable: false,
  searchInput: undefined,
  onBlur: undefined,
  allowCustomInput: true
})

const emit = defineEmits<{
  'update:modelValue': [value: LocationItem | undefined]
  'blur': []
}>()

const isOpen = ref(false)
const inputRef = ref<HTMLInputElement | null>(null)
const dropdownRef = ref<HTMLDivElement | null>(null)
const isSearching = ref(false)
const currentInputValue = ref('') // Сохраняем введенное значение

// Отслеживаем изменения в searchInput.modelValue
watch(() => props.searchInput?.modelValue, (newValue) => {
  if (newValue !== undefined && newValue !== currentInputValue.value) {
    currentInputValue.value = newValue
  }
}, { immediate: true })

// Обработка клика вне компонента для закрытия выпадающего списка
onClickOutside(dropdownRef, () => {
  // Сохраняем введенное значение перед сбросом
  if (props.allowCustomInput && currentInputValue.value && currentInputValue.value.trim()) {
    // Проверяем, что значение изменилось
    if (!props.modelValue || props.modelValue.value !== currentInputValue.value.trim()) {
      const newItem: LocationItem = {
        value: currentInputValue.value.trim(),
        label: currentInputValue.value.trim()
      }
      emit('update:modelValue', newItem)
    }
  }
  
  isOpen.value = false
  isSearching.value = false
})

// Обработка выбора элемента
const selectItem = (item: LocationItem) => {
  emit('update:modelValue', item)
  isOpen.value = false
  isSearching.value = false
  currentInputValue.value = '' // Очищаем сохраненное значение
  // Очищаем поле поиска после небольшой задержки, чтобы значение успело сохраниться
  if (props.searchInput) {
    setTimeout(() => {
      props.searchInput['onUpdate:modelValue']('')
    }, 0)
  }
}

// Обработка фокуса на инпуте
const handleFocus = () => {
  if (!props.disabled) {
    isOpen.value = true
    isSearching.value = true
    // При фокусе НЕ восстанавливаем старое значение
    // Это позволяет пользователю вводить новое значение
  }
}

// Обработка потери фокуса
const handleBlur = () => {
  // Даем время для клика вне компонента, чтобы избежать конфликтов
  setTimeout(() => {
    // Если включен ручной ввод и есть введенное значение
    if (props.allowCustomInput && isSearching.value && currentInputValue.value.trim()) {
      // Проверяем, что значение действительно изменилось
      if (!props.modelValue || props.modelValue.value !== currentInputValue.value.trim()) {
        const newItem: LocationItem = {
          value: currentInputValue.value.trim(),
          label: currentInputValue.value.trim()
        }
        selectItem(newItem)
      }
    }
    // Если используется searchInput
    else if (isSearching.value && props.searchInput && currentInputValue.value.trim()) {
      const newItem: LocationItem = {
        value: currentInputValue.value.trim(),
        label: currentInputValue.value.trim()
      }
      // Проверяем, что значение действительно изменилось
      if (!props.modelValue || props.modelValue.value !== newItem.value) {
        selectItem(newItem)
      }
    }
    
    isSearching.value = false
    isOpen.value = false
    
    // Вызываем пользовательский обработчик onBlur
    if (props.onBlur) {
      props.onBlur()
    }
    emit('blur')
  }, 200)
}

// Обработка ввода в поле поиска
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const value = target.value
  
  // Всегда сохраняем введенное значение в currentInputValue
  currentInputValue.value = value
  isSearching.value = true
  
  // Если используется searchInput, обновляем его
  if (props.searchInput) {
    props.searchInput['onUpdate:modelValue'](value)
  }
}

// Обработка клавиш для навигации
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    event.preventDefault()
    isOpen.value = false
    isSearching.value = false
    currentInputValue.value = ''
    if (props.searchInput) {
      props.searchInput['onUpdate:modelValue']('')
    }
  } else if (event.key === 'Enter' && props.searchInput && currentInputValue.value.trim()) {
    event.preventDefault()
    // Создаем новый элемент из введенного текста
    const newItem: LocationItem = {
      value: currentInputValue.value.trim(),
      label: currentInputValue.value.trim()
    }
    selectItem(newItem)
    // Закрываем выпадающий список
    isOpen.value = false
    isSearching.value = false
  } else if (event.key === 'Enter' && !props.searchInput) {
    // Если нет searchInput, просто закрываем список
    event.preventDefault()
    isOpen.value = false
  }
}

// Вычисляемое свойство для отображения значения в инпуте
const displayValue = computed(() => {
  // Если мы ищем и есть введенное значение, показываем его
  if (isSearching.value) {
    if (props.searchInput?.modelValue) {
      return props.searchInput.modelValue
    }
    return currentInputValue.value
  }
  // Иначе показываем выбранное значение
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
          @blur="handleBlur"
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
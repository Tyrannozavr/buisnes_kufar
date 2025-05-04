<script setup lang="ts">
const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value: string) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  text: {
    type: String,
    default: 'Загрузка...'
  },
  fullHeight: {
    type: Boolean,
    default: false
  },
  color: {
    type: String,
    default: 'primary'
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm': return 'h-32'
    case 'md': return 'h-48'
    case 'lg': return 'h-64'
    case 'xl': return 'h-96'
    default: return 'h-48'
  }
})

const spinnerSize = computed(() => {
  switch (props.size) {
    case 'sm': return 'w-6 h-6 border-2'
    case 'md': return 'w-10 h-10 border-3'
    case 'lg': return 'w-16 h-16 border-4'
    case 'xl': return 'w-24 h-24 border-[6px]'
    default: return 'w-10 h-10 border-3'
  }
})

const spinnerColor = computed(() => {
  switch (props.color) {
    case 'primary': return 'border-primary-500'
    case 'secondary': return 'border-gray-500'
    case 'success': return 'border-green-500'
    case 'warning': return 'border-yellow-500'
    case 'error': return 'border-red-500'
    case 'info': return 'border-blue-500'
    default: return 'border-primary-500'
  }
})
</script>

<template>
  <div
:class="[
    'flex flex-col items-center justify-center',
    fullHeight ? 'h-full min-h-[300px]' : sizeClasses
  ]">
    <div
      :class="[
        'spinner rounded-full border-t-transparent animate-spin',
        spinnerSize,
        spinnerColor
      ]"
    />
    <p v-if="text" class="mt-4 text-gray-500">{{ text }}</p>
  </div>
</template>

<style scoped>
.spinner {
  border-style: solid;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
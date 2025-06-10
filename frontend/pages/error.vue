<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

const props = defineProps<{
  error: {
    statusCode?: number
    message?: string
    stack?: string
  }
}>()

const handleError = () => {
  clearError({ redirect: '/' })
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 text-center">
      <div>
        <h1 class="text-9xl font-extrabold text-gray-900">
          {{ error?.statusCode || '500' }}
        </h1>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">
          {{ error?.message || 'Произошла ошибка' }}
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          Что-то пошло не так. Пожалуйста, попробуйте позже или вернитесь на главную страницу.
        </p>
      </div>
      <div class="mt-8">
        <UButton
          color="primary"
          size="lg"
          @click="handleError"
        >
          Вернуться на главную
        </UButton>
      </div>
    </div>
  </div>
</template> 
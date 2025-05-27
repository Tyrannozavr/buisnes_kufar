<template>
  <UContainer>
    <div class="min-h-[60vh] flex flex-col items-center justify-center text-center py-12">
      <h1 class="text-6xl font-bold text-gray-900 mb-4">404</h1>
      <h2 class="text-2xl font-semibold text-gray-700 mb-6">Страница не найдена</h2>
      <p class="text-gray-600 mb-8 max-w-md">
        К сожалению, запрашиваемая страница не существует или была перемещена.
      </p>
      <div class="flex flex-col sm:flex-row gap-4">
        <UButton
          to="/"
          color="primary"
          size="lg"
        >
          Вернуться на главную
        </UButton>
        <UButton
          to="/catalog/products"
          color="neutral"
          size="lg"
        >
          Перейти в каталог
        </UButton>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})

// Очищаем ошибку при монтировании компонента
onMounted(() => {
  clearError()
})
</script> 
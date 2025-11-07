<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// Перенаправляем на страницу администрации, если пользователь попал сюда без ID
onMounted(() => {
  router.push('/profile/administration')
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <div class="text-center">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Редактирование прав доступа</h1>
      <p class="text-gray-600">Перенаправление на страницу администрации...</p>
    </div>
  </div>
</template>

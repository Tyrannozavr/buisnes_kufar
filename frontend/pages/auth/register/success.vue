<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg text-center">
      <div class="flex justify-center">
        <UIcon name="i-heroicons-envelope" class="h-16 w-16 text-primary-600" />
      </div>
      
      <div class="space-y-4">
        <h2 class="text-2xl font-bold tracking-tight text-gray-900">
          Проверьте вашу почту
        </h2>
        
        <p class="text-gray-600">
          Мы отправили письмо с инструкциями для завершения регистрации на указанный email адрес.
        </p>
        
        <p class="text-sm text-gray-500">
          Если вы не получили письмо в течение нескольких минут, проверьте папку "Спам" или попробуйте зарегистрироваться снова.
        </p>
      </div>

      <div class="pt-4">
        <UButton
          to="/auth/login"
          color="primary"
          class="w-full"
        >
          Вернуться на страницу входа
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default'
})
</script> 
<template>
  <UContainer>
    <div class="flex items-center justify-between py-4">
      <!-- Logo and Site Name -->
      <div class="flex items-center space-x-4">
        <NuxtImg 
          src="/images/logo-sm.png"
          alt="БизнесТорг" 
          class="h-12 w-auto"
          loading="eager"
        />
<!--        <h1 class="text-xl font-semibold text-gray-900">БизнесТорг</h1>-->
      </div>

      <!-- Cart Link -->
      <div class="flex items-center">
        <UButton
          to="/cart"
          variant="ghost"
          color="neutral"
          class="flex items-center space-x-2"
        >
          <UIcon name="i-heroicons-shopping-cart" class="h-6 w-6" />
          <span>Корзина</span>
        </UButton>
      </div>

      <!-- Login/Register Button -->
      <div>
        <UButton
          to="/auth/login"
          color="primary"
          variant="solid"
        >
          Вход/Регистрация
        </UButton>
      </div>
    </div>
  </UContainer>
</template>

<script setup lang="ts">
</script>

<style scoped>
/* Additional styles can be added here if needed */
</style>
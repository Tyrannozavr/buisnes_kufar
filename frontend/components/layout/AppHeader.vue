<script setup lang="ts">
import {useUserStore} from '~/stores/user'

const userStore = useUserStore()
</script>
<template>
  <UContainer>
    <div class="flex items-center justify-between py-4">
      <!-- Logo and Site Name -->
      <NuxtLink
          class="flex items-center space-x-4"
          to="/"
      >
        <NuxtImg
            src="/images/logo.png"
            alt="БизнесТорг"
            class="h-12 w-auto"
            loading="eager"
        />
        <h1 class="text-xl font-semibold text-gray-900">БизнесТорг</h1>
      </NuxtLink>

      <!-- Cart Link -->
      <div class="flex items-center">
        <UButton
            to="/cart"
            variant="ghost"
            color="neutral"
            class="flex items-center space-x-2"
        >
          <UIcon name="i-heroicons-shopping-cart" class="h-6 w-6"/>
          <span>Корзина</span>
        </UButton>
      </div>

      <!-- Login/Register Button or Profile Button -->
      <div>
        <UButton
            v-if="!userStore.isAuthenticated"
            to="/auth/login"
            color="primary"
            variant="solid"
        >
          Вход/Регистрация
        </UButton>

        <UButton
            v-else
            to="/profile"
            color="primary"
            variant="ghost"
            class="flex items-center space-x-2"
        >
          <div v-if="userStore.companyLogo" class="h-8 w-8 overflow-hidden rounded-full">
            <NuxtImg
                :src="userStore.companyLogo"
                :alt="userStore.companyName"
                class="h-full w-full object-cover"
            />
          </div>
          <UIcon v-else name="i-heroicons-user-circle" class="h-8 w-8"/>
          <span>{{ userStore.companyName || 'Профиль' }}</span>
        </UButton>
      </div>
    </div>
  </UContainer>
</template>

<style scoped>
/* Additional styles can be added here if needed */
</style>
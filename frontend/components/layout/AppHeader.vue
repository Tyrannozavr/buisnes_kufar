<script setup lang="ts">
import {useUserStore} from '~/stores/user'
import { useRoute } from 'vue-router'
import { computed } from 'vue'

const userStore = useUserStore()
const route = useRoute()

const handleLogout = () => {
  userStore.logout()
  // navigateTo('/auth/login')
}

// Create computed property for login URL with current path as back_url
const loginUrl = computed(() => {
  return `/auth/login?back_url=${encodeURIComponent(route.fullPath)}`
})
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

      <!-- Login/Register Button or Profile Button with Logout Icon -->
      <div class="flex items-center space-x-2">
        <UButton
            v-if="!userStore.isAuthenticated"
            :to="loginUrl"
            color="primary"
            variant="solid"
        >
          Вход/Регистрация
        </UButton>

        <template v-else>
          <!-- Profile Button -->
          <UButton
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

          <!-- Logout Button with Tooltip -->
          <UTooltip text="Выйти">
            <UButton
                color="neutral"
                variant="ghost"
                icon="i-heroicons-arrow-right-on-rectangle"
                class="h-10 w-10 cursor-pointer"
                @click="handleLogout"
            />
          </UTooltip>
        </template>
      </div>
    </div>
  </UContainer>
</template>

<style scoped>
/* Additional styles can be added here if needed */
</style>
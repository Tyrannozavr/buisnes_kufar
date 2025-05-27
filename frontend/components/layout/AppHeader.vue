<script setup lang="ts">
import {useUserStore} from '~/stores/user'
import { useCartStore } from '~/stores/cart'
import { computed } from 'vue'

const userStore = useUserStore()
const cartStore = useCartStore()
const totalItems = computed(() => cartStore.totalUniqueItems)

const handleLogout = () => {
  userStore.logout()
  // navigateTo('/auth/login')
}

// Create computed property for login URL with current path as back_url

</script>
<template>
  <header class="bg-white shadow">
    <UContainer>
      <div class="flex items-center justify-between py-4">
        <!-- Logo and Site Name -->
        <div class="flex items-center space-x-4">
          <NuxtLink
              class="flex items-center space-x-4"
              to="/"
          >
            <NuxtImg
                src="/images/logo.jpg"
                alt="БизнесТорг"
                class="h-12 w-auto mr-0"
                loading="eager"
            />
            <NuxtImg
                src="/images/companyNameWhite.png"
                alt="trade_synergy"
                class="h-14 w-auto"
                loading="eager"
            />
          </NuxtLink>
        </div>

        <!-- Cart Link -->
        <div class="flex items-center">
          <UChip
              v-if="totalItems > 0"
              :text="totalItems"
              color="primary"
              size="xl"
              class="mr-2"
          >
            <UButton
                to="/cart"
                color="neutral"
                variant="ghost"
                size="xl"
                icon="i-heroicons-shopping-cart"
            />
          </UChip>
          <UButton
              v-else
              to="/cart"
              color="neutral"
              size="xl"
              variant="ghost"
              icon="i-heroicons-shopping-cart"
          />
        </div>

        <!-- Login/Register Button or Profile Button with Logout Icon -->
        <div class="flex items-center space-x-2">
          <UButton
              v-if="!userStore.isAuthenticated"
              to="/auth/login"
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

        <!-- Add this color mode toggle button -->
<!--        <UButton-->
<!--          :icon="colorMode.value === 'dark' ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'"-->
<!--          color="neutral"-->
<!--          variant="ghost"-->
<!--          aria-label="Toggle dark mode"-->
<!--          @click="toggleColorMode"-->
<!--        />-->
      </div>
    </UContainer>
  </header>
</template>

<style scoped>
/* Additional styles can be added here if needed */
</style>
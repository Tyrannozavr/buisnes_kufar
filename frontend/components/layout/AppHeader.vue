<script setup lang="ts">
import {useUserStore} from '~/stores/user'
import { useCartStore } from '~/stores/cart'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const userStore = useUserStore()
const cartStore = useCartStore()
const totalItems = computed(() => cartStore.totalUniqueItems)
const route = useRoute()

const handleLogout = async () => {
  await userStore.logout()
  cartStore.clearCart()
  navigateTo('/auth/login')
}

// Props for sidebar state
const props = defineProps<{
  isSidebarOpen: boolean
}>()

const emit = defineEmits<{
  'update:isSidebarOpen': [value: boolean]
}>()

const toggleSidebar = () => {
  emit('update:isSidebarOpen', !props.isSidebarOpen)
}
</script>

<template>
  <header class="bg-white shadow fixed top-0 left-0 right-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
                class="h-14 w-auto hidden sm:block"
                loading="eager"
            />
          </NuxtLink>
        </div>

        <!-- Mobile Menu Button -->
        <UButton
          icon="i-heroicons-bars-3"
          variant="ghost"
          color="neutral"
          class="md:hidden"
          @click="toggleSidebar"
        />

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
              color="neutral"
              variant="solid"
              class="text-sm sm:text-base"
          >
            Вход/Регистрация
          </UButton>

          <template v-else>
            <!-- Profile Button -->
            <UButton
                to="/profile"
                color="neutral"
                variant="ghost"
                class="flex items-center space-x-2"
            >
              <div v-if="userStore.companyLogo" class="h-8 w-8 overflow-hidden rounded-full hidden sm:block">
                <NuxtImg
                    :src="userStore.companyLogo"
                    :alt="userStore.companyName"
                    class="h-full w-full object-cover"
                />
              </div>
              <UIcon name="i-heroicons-user-circle" class="sm:hidden h-8 w-8"/>
              <span class="hidden sm:inline">{{ userStore.companyName || 'Профиль' }}</span>
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
    </div>
  </header>
</template>

<style scoped>
/* Additional styles can be added here if needed */
</style>
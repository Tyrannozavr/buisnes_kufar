<script setup lang="ts">
import {useUserStore} from '~/stores/user'
import { useCartStore } from '~/stores/cart'
import { useChatUnreadStore } from '~/stores/chatUnread'
import { storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const userStore = useUserStore()
const cartStore = useCartStore()
const chatUnreadStore = useChatUnreadStore()
const { chatsWithUnread } = storeToRefs(chatUnreadStore)
const totalItems = computed(() => cartStore.totalUniqueItems)
const unreadChatsBadge = computed(() => {
  if (chatsWithUnread.value <= 0) return ''
  return chatsWithUnread.value > 99 ? '99+' : String(chatsWithUnread.value)
})
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
      <div class="flex items-center justify-between gap-2 py-4">
        <!-- Left: burger (mobile) + logo -->
        <div class="flex min-w-0 items-center gap-1 sm:gap-3">
          <UButton
            icon="i-heroicons-bars-3"
            variant="ghost"
            color="neutral"
            class="md:hidden shrink-0"
            aria-label="Открыть меню"
            @click="toggleSidebar"
          />
          <NuxtLink class="flex min-w-0 items-center" to="/">
            <Logo class="h-10 w-auto max-w-[160px] sm:h-12 sm:max-w-[220px]" />
          </NuxtLink>
        </div>

        <!-- Right: cart + auth -->
        <div class="flex shrink-0 items-center gap-1 sm:gap-2">
          <UChip
              v-if="totalItems > 0"
              :text="totalItems"
              color="primary"
              size="xl"
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
            <div class="relative inline-flex min-w-0">
              <UButton
                  to="/profile"
                  color="neutral"
                  variant="ghost"
                  class="flex items-center gap-2 max-w-[46vw] sm:max-w-none cursor-pointer"
              >
                <div
                  v-if="userStore.companyLogo"
                  class="h-8 w-8 overflow-hidden rounded-full shrink-0"
                >
                  <NuxtImg
                      :src="userStore.companyLogo"
                      :alt="userStore.companyName"
                      class="h-full w-full object-cover"
                  />
                </div>
                <UIcon
                  v-else
                  name="i-heroicons-user-circle"
                  class="h-8 w-8 shrink-0"
                />
                <span class="truncate text-sm sm:text-base">
                  {{ userStore.companyName || 'Профиль' }}
                </span>
              </UButton>
              <ChatUnreadBadge
                  v-if="unreadChatsBadge"
                  :count="unreadChatsBadge"
                  class="absolute -top-0.5 -right-1 pointer-events-none"
              />
            </div>

            <UTooltip text="Выйти">
              <UButton
                  color="neutral"
                  variant="ghost"
                  icon="i-heroicons-arrow-right-on-rectangle"
                  class="h-10 w-10 shrink-0 cursor-pointer"
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
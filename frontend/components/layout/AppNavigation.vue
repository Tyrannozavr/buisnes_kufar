<script setup lang="ts">
import { useRoute } from 'vue-router'
import { ref, computed } from 'vue'
import { useCartStore } from '~/stores/cart'

const route = useRoute()
const cartStore = useCartStore()
const totalItems = computed(() => cartStore.totalUniqueItems)

const navigationItems = [
  { name: 'Главная', path: '/' },
  { name: 'Каталог товаров', path: '/catalog/products' },
  { name: 'Каталог услуг', path: '/catalog/services' },
  { name: 'Производители', path: '/manufacturers' },
  { name: 'Услуги', path: '/service-providers' },
  { name: 'О нас', path: '/about' },
  { name: 'Объявления', path: '/announcements' },
  { name: 'Новости', path: '/companies' }
]

// Function to check if a navigation item is active
const isActive = (path: string): boolean => {
  // Exact match for home page
  if (path === '/' && route.path === '/') {
    return true
  }

  // For other pages, check if the current route starts with the navigation item path
  return path !== '/' && route.path.startsWith(path)
}

// Props for sidebar state
const props = defineProps<{
  isSidebarOpen: boolean
}>()

const emit = defineEmits<{
  'update:isSidebarOpen': [value: boolean]
}>()

const closeSidebar = () => {
  emit('update:isSidebarOpen', false)
}
</script>

<template>
  <!-- Desktop Navigation -->
  <div class="bg-gray-50 border-b hidden md:block">
    <UContainer>
      <nav class="flex justify-between space-x-6 md:space-x-0 py-3">
        <UButton
          v-for="item in navigationItems"
          :key="item.path"
          :to="item.path"
          variant="ghost"
          :color="isActive(item.path) ? 'primary' : 'neutral'"
          class="text-sm"
          :class="isActive(item.path) ? 'font-medium' : ''"
        >
          {{ item.name }}
        </UButton>
      </nav>
    </UContainer>
  </div>

  <!-- Mobile Sidebar -->
  <USlideover 
    :open="isSidebarOpen"
    @update:open="emit('update:isSidebarOpen', $event)"
    side="left" 
    class="md:hidden"
  >
    <template #content>
      <div class="p-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-semibold">Меню</h2>
          <UButton
            icon="i-heroicons-x-mark"
            variant="ghost"
            color="neutral"
            @click="closeSidebar"
          />
        </div>
        <nav class="flex flex-col space-y-2">
          <UButton
            v-for="item in navigationItems"
            :key="item.path"
            :to="item.path"
            variant="ghost"
            :color="isActive(item.path) ? 'primary' : 'neutral'"
            class="justify-start text-sm"
            :class="isActive(item.path) ? 'font-medium' : ''"
            @click="closeSidebar"
          >
            {{ item.name }}
          </UButton>
        </nav>
      </div>
    </template>
  </USlideover>
</template>


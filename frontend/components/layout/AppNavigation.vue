<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const navigationItems = [
  { name: 'Главная', path: '/' },
  { name: 'Каталог товаров', path: '/catalog/products' },
  { name: 'Каталог услуг', path: '/catalog/services' },
  { name: 'Производители', path: '/manufacturers' },
  { name: 'Услуги', path: '/service-providers' },
  { name: 'О нас', path: '/about' },
  { name: 'Объявления', path: '/announcements' },
  { name: 'Новости', path: '/news' }
]

// Function to check if a navigation item is active
const isActive = (path: string): boolean => {
  // Exact match for home page
  if (path === '/' && route.path === '/') {
    return true
  }

  // For other pages, check if the current route starts with the navigation item path
  // This handles nested routes (e.g. /catalog/products/123 should highlight "Каталог товаров")
  return path !== '/' && route.path.startsWith(path)
}
</script>


<template>
  <div class="bg-gray-50 border-b">
    <UContainer>
      <nav class="flex justify-between space-x-6 py-3">
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
</template>


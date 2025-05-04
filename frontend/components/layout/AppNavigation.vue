<template>
  <div class="bg-gray-50 border-b">
    <UContainer>
      <nav class="flex items-center space-x-6 py-3">
        <UButton
          v-for="item in navigationItems"
          :key="item.path"
          :to="item.path"
          variant="ghost"
          color="neutral"
          class="text-sm"
        >
          {{ item.name }}
        </UButton>
      </nav>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
const navigationItems = [
  { name: 'Главная', path: '/' },
  { name: 'Каталог товаров', path: '/catalog/products' },
  { name: 'Каталог услуг', path: '/catalog/services' },
  { name: 'Производители', path: '/manufacturers' },
  { name: 'Услуги', path: '/services' },
  { name: 'О нас', path: '/about' },
  { name: 'Объявления', path: '/announcements' },
  { name: 'Новости', path: '/news' }
]
</script> 
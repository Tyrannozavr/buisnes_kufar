<template>
  <div class="min-h-screen bg-white">
    <!-- Header -->
    <header class="fixed top-0 left-0 right-0 bg-white shadow-sm z-50">
      <div class="container mx-auto px-4">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <NuxtLink to="/" class="flex items-center space-x-2">
            <img src="/logo.png" alt="Logo" class="h-8 w-8" />
            <span class="text-xl font-bold text-gray-900">Business Platform</span>
          </NuxtLink>

          <!-- Navigation -->
          <nav class="hidden md:flex space-x-8">
            <NuxtLink 
              v-for="item in navigationItems" 
              :key="item.path"
              :to="item.path"
              class="text-gray-600 hover:text-gray-900"
              :class="{ 'text-blue-600': $route.path === item.path }"
            >
              {{ item.label }}
            </NuxtLink>
          </nav>

          <!-- Auth/Actions -->
          <div class="flex items-center space-x-4">
            <UButton
              v-if="!isAuthenticated"
              to="/auth/login"
              color="primary"
              variant="ghost"
            >
              Вход/Регистрация
            </UButton>
            <UButton
              v-else
              to="/dashboard"
              color="primary"
              variant="ghost"
            >
              Личный кабинет
            </UButton>
            <UButton
              to="/cart"
              color="primary"
              variant="ghost"
              icon="i-heroicons-shopping-cart"
            />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-16">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const navigationItems = [
  { label: 'Главная', path: '/' },
  { label: 'Каталог товаров', path: '/catalog/products' },
  { label: 'Каталог услуг', path: '/catalog/services' },
  { label: 'Производители', path: '/manufacturers' },
  { label: 'Услуги', path: '/services' },
  { label: 'О нас', path: '/about' },
]

// Mock authentication state - will be replaced with actual auth logic
const isAuthenticated = ref(false)
</script> 
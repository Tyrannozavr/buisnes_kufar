<template>
  <!-- Приложение работает только в светлой теме (см. nuxt.config.ts). -->
  <div class="min-h-screen bg-white text-gray-900 pt-22">
    <AppHeader 
      :isSidebarOpen="isSidebarOpen"
      @update:isSidebarOpen="isSidebarOpen = $event"
    />
    <AppNavigation
      :isSidebarOpen="isSidebarOpen"
      @update:isSidebarOpen="isSidebarOpen = $event"
    />
    <main class="min-h-screen pt-[72px] md:pt-0">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-4 lg:px-8 py-4">
        <slot />
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '~/components/layout/AppHeader.vue'
import AppNavigation from './AppNavigation.vue'
import AppFooter from "~/components/layout/AppFooter.vue"

const isSidebarOpen = ref(false)
</script>
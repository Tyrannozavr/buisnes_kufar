<template>
  <div class="min-h-screen bg-white dark:bg-gray-900 dark:text-white">
    <AppHeader />
    <AppNavigation />
    <main>
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue'
import AppNavigation from './AppNavigation.vue'

// Initialize color mode
const colorMode = useColorMode()
</script>
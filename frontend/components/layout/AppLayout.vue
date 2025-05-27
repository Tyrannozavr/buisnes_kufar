<template>
  <div class="min-h-screen bg-white  dark:text-white">
    <AppHeader />
    <AppNavigation />
    <main class="min-h-screen">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '~/components/layout/AppHeader.vue'
import AppNavigation from './AppNavigation.vue'
import AppFooter from "~/components/layout/AppFooter.vue";
</script>
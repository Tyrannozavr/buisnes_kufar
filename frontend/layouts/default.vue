<template>
  <AppLayout>
    <CookieConsent />
    <slot />
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '~/components/layout/AppLayout.vue'
import CookieConsent from "~/components/CookieConsent.vue";
</script> 
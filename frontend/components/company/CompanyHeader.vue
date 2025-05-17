<script setup lang="ts">
interface CompanyHeaderProps {
  logo: string
  name: string
  country: string
  region: string
  city: string
  activityType: string
}

defineProps<CompanyHeaderProps>()
</script>

<template>
  <div class="bg-white rounded-lg p-6 shadow-sm">
    <div class="flex items-start gap-6">
      <UAvatar
        :src="logo"
        :alt="name"
        size="xl"
        class="flex-shrink-0"
      />
      
      <div class="flex-grow">
        <h1 class="text-2xl font-bold mb-2">{{ name }}</h1>
        
        <div class="flex flex-wrap gap-4 text-gray-600">
          <div class="flex items-center gap-1">
            <UIcon name="i-lucide-map-pin" class="text-gray-400" />
            <span>{{ city }}, {{ region }}, {{ country }}</span>
          </div>
          
          <div class="flex items-center gap-1">
            <UIcon name="i-lucide-briefcase" class="text-gray-400" />
            <span>{{ activityType }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.company-header {
  @apply bg-white rounded-lg p-6 shadow-sm;
}
</style> 
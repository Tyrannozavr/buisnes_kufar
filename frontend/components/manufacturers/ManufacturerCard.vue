<script setup lang="ts">
import type { Company } from '~/types/company'

defineProps<{
  manufacturer: Company
}>()
</script>

<template>
  <UCard class="hover:shadow-lg transition-shadow">
    <div class="flex items-start gap-4">
      <!-- Logo -->
      <div class="w-24 h-24 flex-shrink-0">
        <NuxtImg
          :src="manufacturer.logo || undefined"
          :alt="manufacturer.name"
          class="w-full h-full object-cover rounded-lg"
        />
      </div>

      <!-- Info -->
      <div class="flex-grow">
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-medium">{{ manufacturer.name }}</h3>
            <p class="text-gray-600">{{ manufacturer.description }}</p>
          </div>
          <UButton
            color="primary"
            variant="soft"
            :to="`/company/${manufacturer.id}`"
          >
            Написать сообщение
          </UButton>
        </div>

        <!-- Location -->
        <div class="mt-2 text-sm text-gray-500">
          {{ manufacturer.city }}, {{ manufacturer.region }}, {{ manufacturer.country }}
        </div>

        <!-- Products -->
        <div class="mt-2">
          <UBadge
            v-for="product in manufacturer.products"
            :key="product"
            color="neutral"
            variant="soft"
            class="mr-2"
          >
            {{ product }}
          </UBadge>
        </div>
      </div>
    </div>
  </UCard>
</template> 
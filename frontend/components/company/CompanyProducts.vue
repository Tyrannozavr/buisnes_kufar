<script setup lang="ts">
import { useProductsApi } from '~/api/products'

// API
const { products } = useProductsApi()

// Computed properties for different product states
const activeProducts = computed(() =>
  products.value?.filter(p => !p.isHidden && !p.isDeleted) ?? []
)

</script>

<template>
  <div class="mt-6">
    <UCard>
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Продукция компании</h2>
        </div>
      </template>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard
          v-for="product in activeProducts"
          :key="product.id"
          class="hover:shadow-lg transition-shadow"
        >
          <template #header>
            <NuxtImg
              :src="product.images[0]"
              :alt="product.name"
              class="w-full h-48 object-cover rounded-t-lg"
            />
          </template>
          
          <div class="space-y-2">
            <h3 class="text-lg font-medium">{{ product.name }}</h3>
            <p class="text-gray-600 line-clamp-2">{{ product.description }}</p>
            <div class="flex justify-between items-center">
              <span class="text-lg font-semibold">{{ product.price }} ₽</span>
              <UBadge
                :color="product.type === 'Стандарт' ? 'primary' : 'neutral'"
                variant="soft"
              >
                {{ product.type }}
              </UBadge>
            </div>
          </div>
          
          <template #footer>
            <div class="flex justify-end">
              <UButton
                color="neutral"
                variant="soft"
                :to="`/products/${product.id}`"
              >
                Подробнее
              </UButton>
            </div>
          </template>
        </UCard>
      </div>
    </UCard>
  </div>
</template>
<template>
  <UCard class="h-full">
    <template #header>
      <div class="relative aspect-video">
        <img 
          :src="product.images[0]" 
          :alt="product.name"
          class="w-full h-full object-cover rounded-t-lg"
        />
        <UBadge 
          v-if="product.is_hidden"
          color="neutral"
          class="absolute top-2 right-2"
        >
          Нет в наличии
        </UBadge>
      </div>
    </template>

    <div class="space-y-2">
      <h3 class="text-lg font-semibold">{{ product.name }}</h3>
      <div v-if="!product.is_hidden" class="text-xl font-bold text-primary">
        {{ formatPrice(product.price) }} ₽
      </div>
      <div class="text-sm text-gray-500">
        {{ getCompanyName(product.company_id) }}
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between items-center">
        <UButton
          color="primary"
          variant="ghost"
          :to="`/catalog/items/${product.slug}`"
        >
          Подробнее
        </UButton>
        <UButton
          v-if="!product.is_hidden"
          color="primary"
          @click="$emit('add-to-cart', product)"
        >
          В корзину
        </UButton>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import type { Product } from '~/types/product'

const props = defineProps<{
  product: Product
}>()

defineEmits<{
  'add-to-cart': [product: Product]
}>()

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const getCompanyName = (companyId: number) => {
  // TODO: Implement proper company lookup
  return 'Неизвестная компания'
}
</script> 
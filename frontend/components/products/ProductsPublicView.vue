<script setup lang="ts">
import type {ProductItemPublic} from '~/types/product'
import ProductPublicCard from "~/components/products/ProductPublicCard.vue";

const props = defineProps<{
  products: ProductItemPublic[]
  title: string
}>()


</script>

<template>
  <UCard class="mb-6">
    <template #header>
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <h3 class="text-xl font-semibold">{{ title }}</h3>
        </div>
        <slot name="header-actions" />
      </div>
    </template>

    <div v-if="products.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <ProductPublicCard
        v-for="product in products"
        :key="product.slug"
        :product="product"
      />
    </div>
    <div v-else class="py-8 text-center text-gray-500">
      <slot name="empty-state" />
    </div>
  </UCard>
</template> 
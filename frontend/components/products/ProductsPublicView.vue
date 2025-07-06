<script setup lang="ts">
import type {ProductItemPublic} from '~/types/product'
import ProductPublicCard from "~/components/products/ProductPublicCard.vue";

const props = defineProps<{
  products: ProductItemPublic[]
  title: string
}>()


</script>

<template>
  <div class="products-view">
    <h3>{{ title }}</h3>
    <div v-if="products.length > 0" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <ProductPublicCard
        v-for="product in products"
        :key="product.slug"
        :product="product"
      />
    </div>
    <div v-else>
      Нет продуктов
    </div>
  </div>
</template> 
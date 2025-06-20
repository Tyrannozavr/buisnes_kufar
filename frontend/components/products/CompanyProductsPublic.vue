<script setup lang="ts">
import type {ProductItemPublic} from '~/types/product'
import ProductsPublicView from "~/components/products/ProductsPublicView.vue";

// Props
const props = defineProps<{
  products: ProductItemPublic[]
}>()

// Emits
const emit = defineEmits<{
  refresh: []
}>()


</script>

<template>
  <div class="company-products">
    <template>
      <ProductsPublicView
        :products="products"
        title="Продукция"
      />
    </template>

  </div>
</template>
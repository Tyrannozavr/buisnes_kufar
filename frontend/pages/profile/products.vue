<script setup lang="ts">
import CompanyProducts from "~/components/company/CompanyProducts.vue"
import {getMyProducts} from '~/api/companyOwner'

definePageMeta({
  layout: 'profile'
})

// Fetch company products
const { data: products } = await getMyProducts()
</script>

<template>
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Продукция</h2>
      <CompanyProducts mode="owner" :products="products?.data || []" />
    </div>
  </div>
</template>
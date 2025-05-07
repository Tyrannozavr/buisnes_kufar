<script setup lang="ts">
import CompanyProducts from "~/components/company/CompanyProducts.vue"

definePageMeta({
  layout: 'profile'
})
</script>

<template>
  <ProfileLayout>
    <div class="bg-white shadow rounded-lg p-6">
      <h2 class="text-lg font-medium text-gray-900 mb-4">Продукция</h2>
      <CompanyProducts />
    </div>
  </ProfileLayout>
</template> 
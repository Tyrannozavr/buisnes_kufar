<script setup lang="ts">
import type { Product } from '~/types/product'
import ProductCard from "~/components/company/ProductCard.vue"
import CustomTooltip from "~/components/ui/CustomTooltip.vue"
import { computed } from 'vue'

const props = defineProps<{
  products: Product[]
  title: string
  isHidden?: boolean
  isDeleted?: boolean
}>()

defineEmits<{
  (e: 'edit', product: Product): void
  (e: 'hide', product: Product): void
  (e: 'delete', product: Product): void
  (e: 'restore', product: Product): void
}>()

const getSectionDescription = computed(() => {
  if (props.isDeleted) {
    return 'Удаленные товары не отображаются в каталоге. Их можно восстановить или удалить навсегда.'
  }
  if (props.isHidden) {
    return 'Скрытые товары видны в каталоге с пометкой "Нет в наличии". Это полезно, когда товар временно недоступен, но вы планируете его вернуть в продажу.'
  }
  return 'Активные товары отображаются в каталоге и доступны для заказа. Здесь вы можете управлять их видимостью и редактировать информацию.'
})
</script>

<template>
  <UCard class="mb-6">
    <template #header>
      <div class="flex justify-between items-center">
        <div class="flex items-center gap-2">
          <h3 class="text-xl font-semibold">{{ title }}</h3>
          <CustomTooltip :text="getSectionDescription">
            <UIcon name="i-heroicons-information-circle" class="text-gray-400 hover:text-gray-600 cursor-help" />
          </CustomTooltip>
        </div>
        <slot name="header-actions" />
      </div>
    </template>

    <div v-if="products.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <ProductCard
        v-for="product in products"
        :key="product.id"
        :product="product"
        :is-hidden="isHidden"
        :is-deleted="isDeleted"
        @edit="$emit('edit', product)"
        @hide="$emit('hide', product)"
        @delete="$emit('delete', product)"
        @restore="$emit('restore', product)"
      />
    </div>
    <div v-else class="py-8 text-center text-gray-500">
      <slot name="empty-state" />
    </div>
  </UCard>
</template> 
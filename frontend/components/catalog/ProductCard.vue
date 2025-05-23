<script setup lang="ts">
import type { Product } from '~/types/product'
import { useCart } from '~/composables/useCart'

const props = defineProps<{
  product: Product
}>()

const { handleAddToCart, handleIncreaseQuantity, handleDecreaseQuantity, getQuantity } = useCart()
const quantity = computed(() => getQuantity(props.product.id))

</script>

<template>
  <UCard class="hover:shadow-lg transition-shadow flex flex-col h-full">
    <div class="flex flex-col h-full">
      <!-- Product Image -->
      <NuxtLink
          :to="`/catalog/products/${product.id}`"
          class="w-full aspect-square mb-4"
      >
        <NuxtImg
            :src="product.images.length > 0 ? product.images[0] : '/images/placeholder.png'"
            :alt="product.name"
            class="w-full h-full object-cover rounded-lg"
        />
      </NuxtLink>

      <!-- Product Info -->
      <div class="flex flex-col justify-between flex-grow">
        <div>
          <NuxtLink
              :to="`/catalog/products/${product.id}`"
              class="text-lg font-medium mb-2 block h-14 overflow-hidden"
          >
            <span class="line-clamp-2">{{ product.name }}</span>
          </NuxtLink>
          <p class="text-gray-600 text-sm mb-4 h-10 overflow-hidden">
            <span class="line-clamp-2">{{ product.description }}</span>
          </p>

          <!-- Price -->
          <div class="text-xl font-bold mb-4">
            {{ product.price.toLocaleString('ru-RU') }} ₽
          </div>
        </div>

        <!-- Cart Controls -->
        <div class="pt-4">
          <div v-if="quantity > 0" class="flex items-center justify-between gap-2">
            <UButton
                class="cursor-pointer"
                color="neutral"
                variant="soft"
                icon="i-heroicons-minus"
                @click="() => handleDecreaseQuantity(product.id, quantity)"
            />
            <span class="text-lg font-medium">{{ quantity }}</span>
            <UButton
                class="cursor-pointer"
                color="neutral"
                variant="soft"
                icon="i-heroicons-plus"
                @click="() => handleIncreaseQuantity(product.id, quantity)"
            />
          </div>
          <UButton
              v-else
              color="primary"
              class="cursor-pointer"
              block
              @click="() => handleAddToCart(product)"
          >
            Добавить в корзину
          </UButton>
        </div>
      </div>
    </div>
  </UCard>
</template>
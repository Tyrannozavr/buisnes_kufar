<script setup lang="ts">
import type { Product } from '~/types/product'
import { useCartStore } from '~/stores/cart'
import {useUserStore} from "~/stores/user";
const userStore = useUserStore()

const props = defineProps<{
  product: Product
}>()

const cartStore = useCartStore()
const toast = useToast()

const quantity = computed(() => {
  const item = cartStore.items.find(item => item.product.id === props.product.id)
  return item?.quantity ?? 0
})

const handleAddToCart = async () => {
  if (!userStore.isAuthenticated) {
    toast.add({
      title: 'Требуется авторизация',
      description: 'Пожалуйста, войдите в систему, чтобы добавить товар в корзину',
      color: 'warning'
    })
    return
  }

  try {
    await cartStore.addToCart(props.product)
    toast.add({
      title: 'Успешно',
      description: 'Товар добавлен в корзину',
      color: 'success'
    })
  } catch (error) {
    toast.add({
      title: 'Ошибка',
      description: 'Не удалось добавить товар в корзину',
      color: 'error'
    })
  }
}

const handleIncreaseQuantity = () => {
  cartStore.updateQuantity(props.product.id, quantity.value + 1)
}

const handleDecreaseQuantity = () => {
  if (quantity.value > 1) {
    cartStore.updateQuantity(props.product.id, quantity.value - 1)
  } else {
    cartStore.removeFromCart(props.product.id)
  }
}
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
      <div class="flex-grow">
        <NuxtLink
            :to="`/catalog/products/${product.id}`"
            class="text-lg font-medium mb-2 block"
        >
          {{ product.name }}
        </NuxtLink>
        <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ product.description }}</p>
        
        <!-- Price -->
        <div class="text-xl font-bold mb-4">
          {{ product.price.toLocaleString('ru-RU') }} ₽
        </div>
      </div>

      <!-- Cart Controls -->
      <div class="mt-auto pt-4">
        <div v-if="quantity > 0" class="flex items-center justify-between gap-2">
          <UButton
              color="neutral"
              variant="soft"
              icon="i-heroicons-minus"
              @click="handleDecreaseQuantity"
          />
          <span class="text-lg font-medium">{{ quantity }}</span>
          <UButton
              color="neutral"
              variant="soft"
              icon="i-heroicons-plus"
              @click="handleIncreaseQuantity"
          />
        </div>
        <UButton
            v-else
            color="primary"
            class="cursor-pointer"
            block
            @click="handleAddToCart"
        >
          Добавить в корзину
        </UButton>
      </div>
    </div>
  </UCard>
</template> 
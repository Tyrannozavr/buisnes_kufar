<script setup lang="ts">
import { useCartStore } from '~/stores/cart'
import { useUserStore } from '~/stores/user'
import QuantityControls from '~/components/ui/QuantityControls.vue'

const cartStore = useCartStore()
const userStore = useUserStore()

const handleUpdateQuantity = (productId: string, quantity: number) => {
  cartStore.updateQuantity(productId, quantity)
}

const handleRemoveItem = (productId: string) => {
  cartStore.removeFromCart(productId)
}

const handleClearCart = () => {
  cartStore.clearCart()
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Корзина</h1>
    <!-- Empty Cart -->
    <div v-if="!cartStore.items.length" class="text-center py-12">
      <UIcon name="i-heroicons-shopping-cart" class="h-16 w-16 mx-auto text-gray-400 mb-4"/>
      <h2 class="text-xl font-medium text-gray-900 mb-2">Корзина пуста</h2>
      <p class="text-gray-500 mb-6">Добавьте товары в корзину, чтобы оформить заказ</p>
      <UButton
          to="/catalog/products"
          color="primary"
      >
        Перейти к товарам
      </UButton>
    </div>

    <!-- Cart Items -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Items List -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-lg shadow-sm">
          <div class="divide-y divide-gray-200">
            <div
                v-for="item in cartStore.items"
                :key="item.product.id"
                class="p-6"
            >
              <div class="flex flex-col">
                <!-- Product Image and Info -->
                <div class="flex items-start space-x-4">
                  <NuxtLink
                      :to="`/catalog/products/${item.product.id}`"
                      class="w-24 h-24 flex-shrink-0"
                  >
                    <NuxtImg
                        :src="item.product.images[0]"
                        :alt="item.product.name"
                        class="w-full h-full object-cover rounded-lg"
                    />
                  </NuxtLink>

                  <!-- Product Info -->
                  <div class="flex-grow">
                    <NuxtLink
                        :to="`/catalog/products/${item.product.id}`"
                        class="text-lg font-medium text-gray-900 hover:text-primary-600"
                    >
                      {{ item.product.name }}
                    </NuxtLink>
                    <p class="mt-1 text-sm text-gray-500 line-clamp-2">
                      {{ item.product.description }}
                    </p>
                    <div class="mt-2 text-lg font-medium text-gray-900">
                      {{ item.product.price.toLocaleString('ru-RU') }} ₽
                    </div>
                  </div>
                </div>

                <!-- Controls -->
                <div class="mt-4 flex items-center justify-between">
                  <QuantityControls
                    :quantity="item.quantity"
                    @update:quantity="(qty) => handleUpdateQuantity(item.product.id, qty)"
                    @remove="() => handleRemoveItem(item.product.id)"
                  />
                  <UButton
                      color="error"
                      variant="ghost"
                      icon="i-heroicons-trash"
                      @click="handleRemoveItem(item.product.id)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h2 class="text-lg font-medium text-gray-900 mb-4">Итого</h2>
          <div class="space-y-4">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Товары ({{ cartStore.totalItems }})</span>
              <span class="text-gray-900">{{ cartStore.totalPrice.toLocaleString('ru-RU') }} ₽</span>
            </div>
            <div class="border-t border-gray-200 pt-4">
              <div class="flex justify-between text-lg font-medium">
                <span>Итого к оплате</span>
                <span>{{ cartStore.totalPrice.toLocaleString('ru-RU') }} ₽</span>
              </div>
            </div>
          </div>

          <div class="mt-6 space-y-4">
            <UButton
                v-if="userStore.isAuthenticated"
                color="primary"
                block
                to="/checkout"
            >
              Оформить заказ
            </UButton>
            <UButton
                v-else
                color="primary"
                block
                to="/auth/login"
            >
              Войти для оформления
            </UButton>
            <UButton
                color="neutral"
                variant="soft"
                block
                @click="handleClearCart"
            >
              Очистить корзину
            </UButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
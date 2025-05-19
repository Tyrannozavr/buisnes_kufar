<script setup lang="ts">
import type { Product } from '~/types/product'
import type { Company } from '~/types/company'
import { useCart } from '~/composables/useCart'

const route = useRoute()
const id = route.params.id

// Cart functionality
const { handleAddToCart, handleIncreaseQuantity, handleDecreaseQuantity, getQuantity } = useCart()
const quantity = computed(() => getQuantity(id as string))

// Fetch product data
const { data: product, error: productError, pending: productPending } = await useApi<Product>(`/products/${id}`)

// Fetch company data
const { data: company, error: companyError } = await useApi<Company>(`/companies/${product.value?.companyId}`)

// Format price
const formatPrice = (price: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0
  }).format(price)
}

// Image slider
const currentImageIndex = ref(0)
const setCurrentImage = (index: number) => {
  currentImageIndex.value = index
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading state -->
    <div v-if="productPending" class="max-w-6xl mx-auto">
      <p class="text-center text-gray-500">
        Загрузка информации о продукте...
      </p>
    </div>

    <!-- Error state -->
    <div v-else-if="productError || companyError" class="max-w-6xl mx-auto">
      <p class="text-center text-red-500">
        Произошла ошибка при загрузке информации. Пожалуйста, попробуйте позже.
      </p>
    </div>

    <!-- Product content -->
    <div v-else-if="product" class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6">
          <!-- Image slider -->
          <div class="relative">
            <div class="aspect-w-4 aspect-h-3 rounded-lg overflow-hidden">
              <NuxtImg
                v-if="product.images && product.images.length > 0"
                :src="product.images[currentImageIndex]"
                :alt="product.name"
                class="w-full h-[400px] object-cover"
              />
              <div v-else class="w-full h-[400px] bg-gray-100 flex items-center justify-center">
                <NuxtImg
                  src="/images/placeholder.png"
                  :alt="product.name"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>

            <!-- Thumbnails -->
            <div v-if="product.images && product.images.length > 1" class="mt-4 flex gap-2 overflow-x-auto">
              <button
                v-for="(image, index) in product.images"
                :key="index"
                @click="setCurrentImage(index)"
                class="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
                :class="{ 'ring-2 ring-primary-500': currentImageIndex === index }"
              >
                <NuxtImg
                  :src="image"
                  :alt="`${product.name} - изображение ${index + 1}`"
                  class="w-full h-full object-cover"
                />
              </button>
            </div>
          </div>

          <!-- Product info -->
          <div class="space-y-6">
            <!-- Company info -->
            <div v-if="company" class="flex items-center gap-3">
              <NuxtImg
                :src="company.logo || '/images/default-company.png'"
                :alt="company.name"
                class="w-12 h-12 rounded-lg object-cover"
              />
              <div>
                <h3 class="font-medium">{{ company.name }}</h3>
              </div>
            </div>

            <!-- Product details -->
            <div>
              <h1 class="text-3xl font-bold mb-2">{{ product.name }}</h1>
              <p class="text-2xl font-semibold text-primary-600 mb-4">
                {{ formatPrice(product.price) }}
              </p>
              <p class="text-gray-600">{{ product.description }}</p>
            </div>

            <!-- Article -->
            <div class="border-t pt-4">
              <p class="text-sm text-gray-500">Артикул: {{ product.article }}</p>
            </div>

            <!-- Characteristics -->
            <div class="border-t pt-4">
              <h3 class="font-semibold mb-4">Характеристики</h3>
              <dl class="grid grid-cols-1 gap-4">
                <div v-for="(char, index) in product.characteristics" :key="index" class="flex justify-between py-2 border-b last:border-0">
                  <dt class="text-gray-600">{{ char.name }}</dt>
                  <dd class="font-medium">{{ char.value }}</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>

        <!-- Cart controls - moved outside of product info -->
        <div class="border-t mt-6 p-6">
          <div v-if="quantity > 0" class="flex items-center justify-between gap-2 max-w-xs mx-auto">
            <UButton
              class="cursor-pointer"
              color="neutral"
              variant="soft"
              icon="i-heroicons-minus"
              @click="() => handleDecreaseQuantity(id as string, quantity)"
            />
            <span class="text-lg font-medium">{{ quantity }}</span>
            <UButton
              class="cursor-pointer"
              color="neutral"
              variant="soft"
              icon="i-heroicons-plus"
              @click="() => handleIncreaseQuantity(id as string, quantity)"
            />
          </div>
          <div v-else class="flex justify-center">
            <UButton
              color="primary"
              class="cursor-pointer"
              block
              @click="() => product && handleAddToCart(product)"
            >
              Добавить в корзину
            </UButton>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 
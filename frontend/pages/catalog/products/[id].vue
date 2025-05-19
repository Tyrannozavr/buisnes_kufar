<script setup lang="ts">
interface Product {
  id: string
  companyId: string
  name: string
  description: string
  article: string
  type: string
  price: number
  images: string[]
  characteristics: Array<{
    name: string
    value: string
  }>
}

interface Company {
  id: string
  name: string
  logo: string
}

const route = useRoute()
const id = route.params.id

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
const showNextImage = () => {
  if (product.value?.images) {
    currentImageIndex.value = (currentImageIndex.value + 1) % product.value.images.length
  }
}
const showPrevImage = () => {
  if (product.value?.images) {
    currentImageIndex.value = (currentImageIndex.value - 1 + product.value.images.length) % product.value.images.length
  }
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
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full bg-gray-100 flex items-center justify-center">
                <span class="text-gray-400">Нет изображения</span>
              </div>
            </div>

            <!-- Slider controls -->
            <div v-if="product.images && product.images.length > 1" class="absolute inset-0 flex items-center justify-between p-4">
              <button
                @click="showPrevImage"
                class="bg-white/80 hover:bg-white p-2 rounded-full shadow-md transition-colors"
              >
                <Icon name="heroicons:chevron-left" class="w-6 h-6" />
              </button>
              <button
                @click="showNextImage"
                class="bg-white/80 hover:bg-white p-2 rounded-full shadow-md transition-colors"
              >
                <Icon name="heroicons:chevron-right" class="w-6 h-6" />
              </button>
            </div>

            <!-- Thumbnails -->
            <div v-if="product.images && product.images.length > 1" class="mt-4 flex gap-2 overflow-x-auto">
              <button
                v-for="(image, index) in product.images"
                :key="index"
                @click="currentImageIndex = index"
                class="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden"
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
                <p class="text-sm text-gray-500">Продавец</p>
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
      </div>
    </div>
  </div>
</template> 
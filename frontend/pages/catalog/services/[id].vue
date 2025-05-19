<script setup lang="ts">
interface Service {
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

// Fetch service data
const { data: service, error: serviceError, pending: servicePending } = await useApi<Service>(`/products/${id}`)

// Fetch company data
const { data: company, error: companyError } = await useApi<Company>(`/companies/${service.value?.companyId}`)

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
  if (service.value?.images) {
    currentImageIndex.value = (currentImageIndex.value + 1) % service.value.images.length
  }
}
const showPrevImage = () => {
  if (service.value?.images) {
    currentImageIndex.value = (currentImageIndex.value - 1 + service.value.images.length) % service.value.images.length
  }
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading state -->
    <div v-if="servicePending" class="max-w-6xl mx-auto">
      <p class="text-center text-gray-500">
        Загрузка информации об услуге...
      </p>
    </div>

    <!-- Error state -->
    <div v-else-if="serviceError || companyError" class="max-w-6xl mx-auto">
      <p class="text-center text-red-500">
        Произошла ошибка при загрузке информации. Пожалуйста, попробуйте позже.
      </p>
    </div>

    <!-- Service content -->
    <div v-else-if="service" class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6">
          <!-- Image slider -->
          <div class="relative">
            <div class="aspect-w-4 aspect-h-3 rounded-lg overflow-hidden">
              <NuxtImg
                v-if="service.images && service.images.length > 0"
                :src="service.images[currentImageIndex]"
                :alt="service.name"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full bg-gray-100 flex items-center justify-center">
                <span class="text-gray-400">Нет изображения</span>
              </div>
            </div>

            <!-- Slider controls -->
            <div v-if="service.images && service.images.length > 1" class="absolute inset-0 flex items-center justify-between p-4">
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
            <div v-if="service.images && service.images.length > 1" class="mt-4 flex gap-2 overflow-x-auto">
              <button
                v-for="(image, index) in service.images"
                :key="index"
                @click="currentImageIndex = index"
                class="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden"
                :class="{ 'ring-2 ring-primary-500': currentImageIndex === index }"
              >
                <NuxtImg
                  :src="image"
                  :alt="`${service.name} - изображение ${index + 1}`"
                  class="w-full h-full object-cover"
                />
              </button>
            </div>
          </div>

          <!-- Service info -->
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
                <p class="text-sm text-gray-500">Поставщик услуг</p>
              </div>
            </div>

            <!-- Service details -->
            <div>
              <h1 class="text-3xl font-bold mb-2">{{ service.name }}</h1>
              <p class="text-2xl font-semibold text-primary-600 mb-4">
                {{ formatPrice(service.price) }}
              </p>
              <p class="text-gray-600">{{ service.description }}</p>
            </div>

            <!-- Article -->
            <div class="border-t pt-4">
              <p class="text-sm text-gray-500">Артикул: {{ service.article }}</p>
            </div>

            <!-- Characteristics -->
            <div class="border-t pt-4">
              <h3 class="font-semibold mb-4">Характеристики услуги</h3>
              <dl class="grid grid-cols-1 gap-4">
                <div v-for="(char, index) in service.characteristics" :key="index" class="flex justify-between py-2 border-b last:border-0">
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
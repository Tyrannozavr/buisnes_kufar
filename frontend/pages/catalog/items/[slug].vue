<script setup lang="ts">
import type { Product, ProductItemPublic } from '~/types/product'
import type { Service } from '~/types/service'
import { useCart } from '~/composables/useCart'
import { useCompaniesApi } from '~/api'

const route = useRoute()
const slug = computed(() => route.params.slug as string)

const { data: item, error: itemError, pending: itemPending } = await useAsyncData(
  () => `catalog-item-${slug.value}`,
  () => {
    const { $api } = useNuxtApp()
    return $api.get<Product | Service>(`/v1/products/slug/${slug.value}`)
  },
  { watch: [slug] },
)

const companyId = computed(() => item.value?.company_id ?? null)

const { data: company, error: companyError } = await useAsyncData(
  () => `catalog-item-company-${companyId.value ?? 'none'}`,
  async () => {
    if (!companyId.value) return null
    const { getCompanyById } = useCompaniesApi()
    return await getCompanyById(companyId.value)
  },
  { watch: [companyId] },
)

const { handleAddToCart, handleIncreaseQuantity, handleDecreaseQuantity, getQuantity } = useCart()
const quantity = computed(() => getQuantity(slug.value))

const formatPrice = (price: number) => {
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    maximumFractionDigits: 0,
  }).format(price)
}

const currentImageIndex = ref(0)
const setCurrentImage = (index: number) => {
  currentImageIndex.value = index
}

const handleAddToCartClick = () => {
	const cartProduct = toCartProduct()
	if (cartProduct) {
		handleAddToCart(cartProduct)
	}
}

const toCartProduct = (): ProductItemPublic | null => {
	if (!item.value) return null

	const raw = item.value as Product & { company_id?: number; images?: string[] }
	return {
		name: raw.name,
		logo_url: raw.images?.[0] ?? null,
		slug: raw.slug,
		description: raw.description ?? '',
		article: raw.article,
		type: raw.type as ProductItemPublic['type'],
		price: raw.price,
		unit_of_measurement: raw.unit_of_measurement ?? 'шт',
		company_id: raw.company_id ?? companyId.value ?? 0,
		company_name: company.value?.name ?? '',
		company_slug: company.value?.slug ?? undefined,
	}
}
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Loading state -->
    <div v-if="itemPending" class="max-w-6xl mx-auto">
      <p class="text-center text-gray-500">
        Загрузка информации...
      </p>
    </div>
    <!-- Error state -->
    <div v-else-if="itemError || companyError" class="max-w-6xl mx-auto">
      <p class="text-center text-red-500">
        Произошла ошибка при загрузке информации. Пожалуйста, попробуйте позже.
      </p>
    </div>

    <!-- Item content -->
    <div v-else-if="item" class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-sm overflow-hidden">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6">
          <!-- Image slider -->
          <div class="relative">
            <div class="aspect-w-4 aspect-h-3 rounded-lg overflow-hidden">
              <NuxtImg
                v-if="item.images && item.images.length > 0"
                :src="item.images[currentImageIndex]"
                :alt="item.name"
                class="w-full h-auto object-contain"
              />
              <div v-else class="w-full h-[400px] bg-gray-100 flex items-center justify-center">
                <NuxtImg
                  src="/images/placeholder.png"
                  :alt="item.name"
                  class="w-full h-full object-cover"
                />
              </div>
            </div>

            <!-- Thumbnails -->
            <div v-if="item.images && item.images.length > 1" class="mt-4 flex gap-2 overflow-x-auto">
              <button
                v-for="(image, index) in item.images"
                :key="index"
                @click="setCurrentImage(index)"
                class="w-20 h-20 flex-shrink-0 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
                :class="{ 'ring-2 ring-primary-500': currentImageIndex === index }"
              >
                <NuxtImg
                  :src="image"
                  :alt="`${item.name} - изображение ${index + 1}`"
                  class="w-full h-full object-cover"
                />
              </button>
            </div>
          </div>

          <!-- Item info -->
          <div class="space-y-6">
            <!-- Company info -->
            <NuxtLink
                v-if="company"
                :to="`/companies/${company.slug}`"
                class="flex items-center gap-3"
            >
              <NuxtImg
                :src="company.logo_url || '/images/default-company-logo.png'"
                :alt="company.name"
                class="w-12 h-12 rounded-lg object-cover"
              />
              <div>
                <h3 class="font-medium">{{ company.name }}</h3>
              </div>
            </NuxtLink>

            <!-- Item details -->
            <div>
              <h1 class="text-3xl font-bold mb-2">{{ item.name }}</h1>
              <div class="flex justify-between gap-4 mb-4">
                <p class="text-2xl font-semibold text-primary-600">
                  {{ formatPrice(item.price) }}
                </p>
                <ClientOnly>
                  <div v-if="quantity > 0" class="flex items-center gap-2">
                    <UButton
                      class="cursor-pointer"
                      color="neutral"
                      variant="soft"
                      icon="i-heroicons-minus"
                      size="sm"
                      @click="() => handleDecreaseQuantity(slug, quantity)"
                    />
                    <span class="text-lg font-medium">{{ quantity }}</span>
                    <UButton
                      class="cursor-pointer"
                      color="neutral"
                      variant="soft"
                      icon="i-heroicons-plus"
                      size="sm"
                      @click="() => handleIncreaseQuantity(slug, quantity)"
                    />
                  </div>
                  <div v-else>
                    <UButton
                      color="primary"
                      class="cursor-pointer"
                      size="sm"
                      @click="handleAddToCartClick"
                    >
                      Добавить в корзину
                    </UButton>
                  </div>
                </ClientOnly>
              </div>
              <p class="text-gray-600">{{ item.description }}</p>
            </div>

            <!-- Article -->
            <div class="border-t pt-4">
              <p class="text-sm text-gray-500">Артикул: {{ item.article }}</p>
            </div>

            <!-- Characteristics -->
            <div class="border-t pt-4">
              <h3 class="font-semibold mb-4">Характеристики</h3>
              <dl class="grid grid-cols-1 gap-4">
                <div v-for="(char, index) in item.characteristics" :key="index" class="flex justify-between py-2 border-b last:border-0">
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

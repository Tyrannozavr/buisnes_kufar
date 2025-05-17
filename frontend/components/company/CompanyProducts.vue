<script setup lang="ts">
import type { Product } from '~/types/product'
import { useProductsApi } from '~/api/products'

// State
const showProductForm = ref(false)
const selectedProduct = ref<Product | null>(null)

// API
const { products, refresh, hideProduct, deleteProduct, restoreProduct, saveProduct } = useProductsApi()

// Computed properties for different product states
const activeProducts = computed(() =>
  products.value?.filter(p => !p.isHidden && !p.isDeleted) ?? []
)

const hiddenProducts = computed(() =>
  products.value?.filter(p => p.isHidden && !p.isDeleted) ?? []
)

const deletedProducts = computed(() =>
  products.value?.filter(p => p.isDeleted) ?? []
)

// Product management methods
const openProductForm = (product?: Product) => {
  selectedProduct.value = product || null
  showProductForm.value = true
}

const closeProductForm = () => {
  selectedProduct.value = null
  showProductForm.value = false
}

const editProduct = (product: Product) => {
  openProductForm(product)
}

const handleHideProduct = async (product: Product) => {
  await hideProduct(product.id)
}

const handleDeleteProduct = async (product: Product) => {
  await deleteProduct(product.id)
}

const handleRestoreProduct = async (product: Product) => {
  await restoreProduct(product.id)
}

const handleSaveProduct = async (productData: Partial<Product>) => {
  const success = await saveProduct(productData, selectedProduct.value?.id)
  if (success) {
    closeProductForm()
  }
}
</script>

<template>
  <div class="mt-6">
    <UCard>
      <template #header>
        <div class="flex justify-between items-center">
          <h2 class="text-xl font-semibold">Продукция компании</h2>
          <UButton
            color="primary"
            variant="soft"
            @click="openProductForm()"
          >
            Добавить продукт
          </UButton>
        </div>
      </template>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard
          v-for="product in activeProducts"
          :key="product.id"
          class="hover:shadow-lg transition-shadow"
        >
          <template #header>
            <img
              :src="product.images[0]"
              :alt="product.name"
              class="w-full h-48 object-cover rounded-t-lg"
            />
          </template>
          
          <div class="space-y-2">
            <h3 class="text-lg font-medium">{{ product.name }}</h3>
            <p class="text-gray-600 line-clamp-2">{{ product.description }}</p>
            <div class="flex justify-between items-center">
              <span class="text-lg font-semibold">{{ product.price }} ₽</span>
              <UBadge
                :color="product.type === 'Стандарт' ? 'primary' : 'neutral'"
                variant="soft"
              >
                {{ product.type }}
              </UBadge>
            </div>
          </div>
          
          <template #footer>
            <div class="flex justify-between">
              <UButton
                color="neutral"
                variant="soft"
                :to="`/products/${product.id}`"
              >
                Подробнее
              </UButton>
              <UButton
                color="primary"
                variant="soft"
                @click="editProduct(product)"
              >
                Редактировать
              </UButton>
            </div>
          </template>
        </UCard>
      </div>
    </UCard>
  </div>
</template>
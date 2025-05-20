<script setup lang="ts">
import type { Product } from '~/types/product'
import ProductCard from "~/components/company/ProductCard.vue"
import ProductForm from "~/components/company/ProductForm.vue"

const props = defineProps<{
  products: Product[]
  mode?: 'client' | 'owner'
}>()

// State
const showProductForm = ref(false)
const selectedProduct = ref<Product | null>(null)

// Computed properties for different product states
const activeProducts = computed(() =>
  props.products.filter(p => !p.isHidden && !p.isDeleted)
)

const hiddenProducts = computed(() =>
  props.products.filter(p => p.isHidden && !p.isDeleted)
)

const deletedProducts = computed(() =>
  props.products.filter(p => p.isDeleted)
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

const hideProduct = async (product: Product) => {
  try {
    await useApi(`/products/${product.id}/hide`, {
      method: 'PUT'
    })
    useToast().add({
      title: 'Успешно',
      description: 'Продукт скрыт',
      color: 'success'
    })
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось скрыть продукт',
      color: 'error'
    })
  }
}

const deleteProduct = async (product: Product) => {
  try {
    await useApi(`/products/${product.id}/delete`, {
      method: 'PUT'
    })
    useToast().add({
      title: 'Успешно',
      description: 'Продукт удален',
      color: 'success'
    })
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось удалить продукт',
      color: 'error'
    })
  }
}

const restoreProduct = async (product: Product) => {
  try {
    await useApi(`/products/${product.id}/restore`, {
      method: 'PUT'
    })
    useToast().add({
      title: 'Успешно',
      description: 'Продукт восстановлен',
      color: 'success'
    })
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось восстановить продукт',
      color: 'error'
    })
  }
}

const saveProduct = async (productData: Partial<Product>) => {
  try {
    if (selectedProduct.value) {
      // Update existing product
      await useApi(`/products/${selectedProduct.value.id}`, {
        method: 'PUT',
        body: productData
      })
      useToast().add({
        title: 'Успешно',
        description: 'Продукт обновлен',
        color: 'success'
      })
    } else {
      // Create new product
      await useApi('/products', {
        method: 'POST',
        body: productData
      })
      useToast().add({
        title: 'Успешно',
        description: 'Продукт добавлен',
        color: 'success'
      })
    }
    closeProductForm()
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось сохранить продукт',
      color: 'error'
    })
  }
}
</script>

<template>
  <div class="company-products">
    <!-- Client Mode -->
    <template v-if="mode === 'client'">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <UCard
          v-for="product in activeProducts"
          :key="product.id"
          class="hover:shadow-lg transition-shadow"
        >
          <template #header>
            <NuxtImg
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
                color="neutral"
                variant="soft"
              >
                {{ product.type }}
              </UBadge>
            </div>
          </div>
          
          <template #footer>
            <div class="flex justify-end">
              <UButton
                color="neutral"
                variant="soft"
                :to="`/catalog/products/${product.id}`"
              >
                Подробнее
              </UButton>
            </div>
          </template>
        </UCard>
      </div>
    </template>

    <!-- Owner Mode -->
    <template v-else>
      <UCard class="mb-6">
        <template #header>
          <div class="flex justify-between items-center">
            <h3 class="text-xl font-semibold">Активная продукция</h3>
            <UButton
              color="primary"
              icon="i-heroicons-plus"
              @click="openProductForm"
            >
              Добавить продукт
            </UButton>
          </div>
        </template>
        <!-- Active Products -->
        <div v-if="activeProducts.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <ProductCard
            v-for="product in activeProducts"
            :key="product.id"
            :product="product"
            @edit="editProduct"
            @hide="hideProduct"
            @delete="deleteProduct"
          />
        </div>
        <div v-else class="py-8 text-center text-gray-500">
          <UIcon name="i-heroicons-cube" class="mx-auto mb-2 h-12 w-12"/>
          <p>У вас пока нет добавленных продуктов</p>
          <UButton
            color="primary"
            icon="i-heroicons-plus"
            class="mt-4"
            @click="openProductForm"
          >
            Добавить продукт
          </UButton>
        </div>
      </UCard>

      <!-- Hidden Products -->
      <UCard v-if="hiddenProducts.length > 0" class="mb-6">
        <template #header>
          <h3 class="text-xl font-semibold">Скрытая продукция</h3>
        </template>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <ProductCard
            v-for="product in hiddenProducts"
            :key="product.id"
            :product="product"
            :is-hidden="true"
            @restore="restoreProduct"
            @delete="deleteProduct"
          />
        </div>
      </UCard>

      <!-- Deleted Products -->
      <UCard v-if="deletedProducts.length > 0">
        <template #header>
          <h3 class="text-xl font-semibold">Удаленная продукция</h3>
        </template>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <ProductCard
            v-for="product in deletedProducts"
            :key="product.id"
            :product="product"
            :is-deleted="true"
            @restore="restoreProduct"
          />
        </div>
      </UCard>

      <!-- Product Form Modal -->
      <ProductForm
        v-model="showProductForm"
        :product="selectedProduct"
        @save="saveProduct"
      />
    </template>
  </div>
</template>
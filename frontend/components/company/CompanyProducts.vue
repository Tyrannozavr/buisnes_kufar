<script setup lang="ts">
import type { Product } from '~/types/product'
import ProductForm from "~/components/company/ProductForm.vue"
import ProductsView from "~/components/company/ProductsView.vue"

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
      <ProductsView
        :products="activeProducts"
        title="Продукция"
      />
    </template>

    <!-- Owner Mode -->
    <template v-else>
      <!-- Active Products -->
      <ProductsView
        :products="activeProducts"
        title="Активная продукция"
        @edit="editProduct"
        @hide="hideProduct"
        @delete="deleteProduct"
      >
        <template #header-actions>
          <UButton
            color="primary"
            icon="i-heroicons-plus"
            @click="() => openProductForm()"
          >
            Добавить продукт
          </UButton>
        </template>
        <template #empty-state>
          <UIcon name="i-heroicons-cube" class="mx-auto mb-2 h-12 w-12"/>
          <p>У вас пока нет добавленных продуктов</p>
          <UButton
            color="primary"
            icon="i-heroicons-plus"
            class="mt-4"
            @click="() => openProductForm()"
          >
            Добавить продукт
          </UButton>
        </template>
      </ProductsView>

      <!-- Hidden Products -->
      <ProductsView
        v-if="hiddenProducts.length > 0"
        :products="hiddenProducts"
        title="Скрытая продукция"
        :is-hidden="true"
        @restore="restoreProduct"
        @delete="deleteProduct"
      />

      <!-- Deleted Products -->
      <ProductsView
        v-if="deletedProducts.length > 0"
        :products="deletedProducts"
        title="Удаленная продукция"
        :is-deleted="true"
        @restore="restoreProduct"
      />

      <!-- Product Form Modal -->
      <ProductForm
        v-model="showProductForm"
        :product="selectedProduct"
        @save="saveProduct"
      />
    </template>
  </div>
</template>
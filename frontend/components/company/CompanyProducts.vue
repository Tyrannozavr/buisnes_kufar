<script setup lang="ts">
import type { Product } from '~/types/product'
import type { ProductCreate, ProductUpdate } from '~/api/me/products'
import { 
  hideProduct as hideProductApi,
  deleteProduct as deleteProductApi,
  restoreProduct as restoreProductApi,
  createProduct,
  createProductWithImages,
  updateProduct,
  toggleProductHidden
} from '~/api/me/products'
import ProductForm from "~/components/company/ProductForm.vue"
import ProductsView from "~/components/company/ProductsView.vue"
import ProductsPublicView from "~/components/products/ProductsPublicView.vue";

// Props
const props = defineProps<{
  products: Product[]
  mode?: 'client' | 'owner'
}>()

// Emits
const emit = defineEmits<{
  refresh: []
}>()

// State
const showProductForm = ref(false)
const selectedProduct = ref<Product | null>(null)

// Computed properties for different product states
const activeProducts = computed(() =>
  props.products.filter(p => !p.is_hidden && !p.is_deleted)
)

const hiddenProducts = computed(() =>
  props.products.filter(p => p.is_hidden && !p.is_deleted)
)

const deletedProducts = computed(() =>
  props.products.filter(p => p.is_deleted)
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
    await hideProductApi(product.id)
    useToast().add({
      title: 'Успешно',
      description: 'Продукт скрыт',
      color: 'success'
    })
    // Emit event to refresh products
    emit('refresh')
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
    await deleteProductApi(product.id)
    useToast().add({
      title: 'Успешно',
      description: 'Продукт удален',
      color: 'success'
    })
    // Emit event to refresh products
    emit('refresh')
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
    await restoreProductApi(product.id)
    useToast().add({
      title: 'Успешно',
      description: 'Продукт восстановлен',
      color: 'success'
    })
    // Emit event to refresh products
    emit('refresh')
  } catch (error) {
    console.error(error)
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось восстановить продукт',
      color: 'error'
    })
  }
}

const saveProduct = async (productData: ProductCreate | ProductUpdate | (ProductCreate & { files?: File[] })) => {
  try {
    if (selectedProduct.value) {
      // Update existing product
      await updateProduct(selectedProduct.value.id, productData as ProductUpdate)
      useToast().add({
        title: 'Успешно',
        description: 'Продукт обновлен',
        color: 'success'
      })
      closeProductForm()
    } else {
      // Create new product
      const data = productData as ProductCreate & { files?: File[] }
      const files = data.files || []
      
      if (files.length > 0) {
        // Создаем продукт с изображениями
        const { files: _, ...productDataWithoutFiles } = data
        const newProduct = await createProductWithImages(productDataWithoutFiles, files)
        useToast().add({
          title: 'Успешно',
          description: 'Продукт с изображениями добавлен',
          color: 'success'
        })
        closeProductForm()
      } else {
        // Создаем продукт без изображений
        const { files: _, ...productDataWithoutFiles } = data
        const newProduct = await createProduct(productDataWithoutFiles)
        useToast().add({
          title: 'Успешно',
          description: 'Продукт добавлен. Теперь вы можете загрузить изображения.',
          color: 'success'
        })
        
        // Если это новый продукт, открываем форму для загрузки изображений
        if (newProduct) {
          selectedProduct.value = newProduct
          // Не закрываем форму, чтобы пользователь мог загрузить изображения
          return
        }
        closeProductForm()
      }
    }
    // Emit event to refresh products
    emit('refresh')
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
      <ProductsPublicView
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
            size="sm"
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
        @done="closeProductForm"
      />
    </template>
  </div>
</template>
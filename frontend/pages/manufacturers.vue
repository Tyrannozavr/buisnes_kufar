<script setup lang="ts">
const route = useRoute()
const title = ref('Производители товаров:\n')
const description = ref('Список производителей товаров.')
const { $api } = useNuxtApp()

// Success message handling
const showSuccessMessage = ref(false)
const successMessage = ref('')

// Fetch manufacturers from the API
const { data: manufacturers, error } = await useAsyncData('manufacturers', () =>
  $api.get('/manufacturers')
)

// For demonstration, keeping the products array
const products = ref([
  { id: 1, name: 'Product A', price: 100 },
  { id: 2, name: 'Product B', price: 200 },
  { id: 3, name: 'Product C', price: 300 },
])

onMounted(() => {
  // Check if there's a success message in the query parameters
  if (route.query.created === 'true') {
    successMessage.value = 'Производитель успешно добавлен'
    showSuccessMessage.value = true

    // Auto-hide the message after 5 seconds
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 5000)
  }
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <!-- Success message notification -->
    <div v-if="showSuccessMessage" class="mb-6">
      <UAlert
        variant="solid"
        color="green"
        title="Успешно!"
        :description="successMessage"
        class="mb-4"
        icon="i-heroicons-check-circle"
      >
        <template #footer>
          <div class="flex justify-end">
            <UButton
              color="white"
              variant="ghost"
              size="sm"
              @click="showSuccessMessage = false"
            >
              Закрыть
            </UButton>
          </div>
        </template>
      </UAlert>
    </div>

    <h1 class="text-2xl font-bold mb-4">{{ title }}</h1>
    <p class="mb-6">{{ description }}</p>

    <!-- Display error if API request failed -->
    <UAlert v-if="error" color="red" variant="soft" class="mb-4">
      Не удалось загрузить данные о производителях
    </UAlert>

    <!-- Products list -->
    <div class="mb-8">
      <h2 class="text-xl font-semibold mb-3">Товары</h2>
      <ul class="list-disc pl-5">
        <li v-for="product in products" :key="product.id" class="mb-2">
          {{ product.name }} - {{ product.price }} руб.
        </li>
      </ul>
    </div>

    <!-- Manufacturers list -->
    <div v-if="manufacturers" class="mb-8">
      <h2 class="text-xl font-semibold mb-3">Производители</h2>
      <ul class="list-disc pl-5">
        <li v-for="manufacturer in manufacturers" :key="manufacturer.id" class="mb-2">
          {{ manufacturer.name }}
        </li>
      </ul>
    </div>

    <!-- Add manufacturer form -->
    <ManufacturerForm />
  </div>
</template>

<style scoped>
/* Custom styles can be added here */
</style>
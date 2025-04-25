<script setup lang="ts">
const route = useRoute()
const showSuccessMessage = ref(false)
const successMessage = ref('')

onMounted(() => {
  // Check if there's a success message in the query parameters
  if (route.query.registered === 'true') {
    successMessage.value = 'Регистрация прошла успешно'
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

    <h1 class="text-2xl font-bold mb-6">Личный кабинет</h1>

    <!-- Profile content goes here -->
    <div class="bg-white rounded-lg shadow p-6">
      <p class="text-gray-700">Добро пожаловать в личный кабинет!</p>
      <!-- Additional profile content can be added here -->
    </div>
  </div>
</template>

<style scoped>
/* Custom styles can be added here */
</style>
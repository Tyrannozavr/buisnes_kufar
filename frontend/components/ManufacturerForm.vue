<script setup lang="ts">
const { $api } = useNuxtApp()
const router = useRouter()

const form = reactive({
  name: '',
  description: '',
  website: ''
})

const isSubmitting = ref(false)
const error = ref(null)

async function submitForm() {
  isSubmitting.value = true
  error.value = null

  try {
    // This request will be made directly from the client
    await $api.post('/manufacturers', form)

    // Redirect to companies page with success message
    router.push({
      path: '/companies',
      query: { created: 'true' }
    })
  } catch (err) {
    error.value = err.message || 'Произошла ошибка при создании производителя'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow p-6">
    <h2 class="text-xl font-semibold mb-4">Добавить производителя</h2>

    <UAlert v-if="error" color="red" variant="soft" class="mb-4">
      {{ error }}
    </UAlert>

    <form @submit.prevent="submitForm">
      <div class="mb-4">
        <UFormField label="Название" required>
          <UInput v-model="form.name" placeholder="Введите название производителя" />
        </UFormField>
      </div>

      <div class="mb-4">
        <UFormField label="Описание">
          <UTextarea v-model="form.description" placeholder="Введите описание" />
        </UFormField>
      </div>

      <div class="mb-6">
        <UFormField label="Веб-сайт">
          <UInput v-model="form.website" placeholder="https://example.com" />
        </UFormField>
      </div>

      <div class="flex justify-end">
        <UButton type="submit" color="primary" :loading="isSubmitting">
          Создать
        </UButton>
      </div>
    </form>
  </div>
</template>
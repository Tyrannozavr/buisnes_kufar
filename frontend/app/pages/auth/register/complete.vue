<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900">Завершение регистрации</h2>
        <p class="mt-2 text-sm text-gray-600">Шаг 2 из 2</p>
      </div>
      
      <div v-if="!isTokenValid" class="text-center text-red-600">
        <p>Недействительная ссылка для регистрации.</p>
        <NuxtLink
          to="/auth/register"
          class="text-primary-600 hover:text-primary-500"
        >
          Вернуться к регистрации
        </NuxtLink>
      </div>

      <form v-else class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="flex flex-col space-y-4 w-full">
          <UFormGroup label="ИНН">
            <UInput
              v-model="form.inn"
              type="text"
              placeholder="Введите ИНН"
              :rules="[rules.required, rules.inn]"
              @update:model-value="validateForm"
              class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Название компании">
            <UInput
              v-model="form.companyName"
              type="text"
              placeholder="Введите название компании"
              :rules="[rules.required]"
              @update:model-value="validateForm"
              class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Адрес">
            <UInput
              v-model="form.address"
              type="text"
              placeholder="Введите адрес"
              :rules="[rules.required]"
              @update:model-value="validateForm"
              class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Пароль">
            <UInput
              v-model="form.password"
              type="password"
              placeholder="Введите пароль"
              :rules="[rules.required, rules.password]"
              @update:model-value="validateForm"
              class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Подтверждение пароля">
            <UInput
              v-model="form.confirmPassword"
              type="password"
              placeholder="Повторите пароль"
              :rules="[rules.required, rules.confirmPassword]"
              @update:model-value="validateForm"
              class="w-full"
            />
          </UFormGroup>
        </div>

        <UButton
          type="submit"
          :color="isFormValid ? 'primary' : 'error'"
          :disabled="!isFormValid"
          :loading="isLoading"
          class="w-full"
        >
          Завершить регистрацию
        </UButton>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const router = useRouter()

const form = ref({
  inn: '',
  companyName: '',
  address: '',
  password: '',
  confirmPassword: ''
})

const isFormValid = ref(false)
const isLoading = ref(false)
const isTokenValid = ref(false)

const rules = {
  required: (value: string) => !!value || 'Обязательное поле',
  inn: (value: string) => {
    if (!value) return true
    return /^\d{10}$/.test(value) || 'ИНН должен содержать 10 цифр'
  },
  password: (value: string) => {
    if (!value) return true
    return value.length >= 6 || 'Пароль должен содержать минимум 6 символов'
  },
  confirmPassword: (value: string) => {
    if (!value) return true
    return value === form.value.password || 'Пароли не совпадают'
  }
}

const validateForm = () => {
  isFormValid.value = !!form.value.inn && 
    !!form.value.companyName && 
    !!form.value.address &&
    !!form.value.password &&
    !!form.value.confirmPassword &&
    rules.inn(form.value.inn) === true &&
    rules.password(form.value.password) === true &&
    rules.confirmPassword(form.value.confirmPassword) === true
}

// Check token validity on page load
onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    isTokenValid.value = false
    return
  }

  try {
    // Mock API call to validate token
    await new Promise(resolve => setTimeout(resolve, 1000))
    // In real app, this would check if the token is valid in the backend
    isTokenValid.value = true
  } catch (error) {
    console.error('Token validation error:', error)
    isTokenValid.value = false
  }
})

const handleSubmit = async () => {
  if (!isFormValid.value) return
  
  isLoading.value = true
  try {
    // Mock API call to complete registration
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // In real app, this would save the data to the database
    // and create the user account
    
    // Redirect to login page with success message
    router.push({
      path: '/auth/login',
      query: { registered: 'true' }
    })
  } catch (error) {
    console.error('Registration completion error:', error)
  } finally {
    isLoading.value = false
  }
}
</script> 
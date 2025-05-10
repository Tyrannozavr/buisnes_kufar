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
              :color="innError ? 'error' : undefined"
              @update:model-value="validateInn"
              class="w-full"
            />
            <p v-if="innError" class="mt-1 text-sm text-red-500">{{ innError }}</p>
          </UFormGroup>
          <UFormGroup label="Должность">
            <UInput
              v-model="form.position"
              type="text"
              placeholder="Введите должность"
              :color="positionError ? 'error' : undefined"
              @update:model-value="validatePosition"
              class="w-full"
            />
            <p v-if="positionError" class="mt-1 text-sm text-red-500">{{ positionError }}</p>
          </UFormGroup>

          <UFormGroup label="Пароль">
            <div class="relative">
              <UInput
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="Введите пароль"
                :color="passwordError ? 'error' : undefined"
                @update:model-value="validatePassword"
                class="w-full pr-10"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                @click="showPassword = !showPassword"
              >
                <UIcon
                  :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  class="h-5 w-5 text-gray-400"
                />
              </button>
            </div>
            <p v-if="passwordError" class="mt-1 text-sm text-red-500">{{ passwordError }}</p>
          </UFormGroup>

          <UFormGroup label="Повторите пароль">
            <div class="relative">
              <UInput
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="Повторите пароль"
                :color="confirmPasswordError ? 'error' : undefined"
                @update:model-value="validateConfirmPassword"
                class="w-full pr-10"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <UIcon
                  :name="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                  class="h-5 w-5 text-gray-400"
                />
              </button>
            </div>
            <p v-if="confirmPasswordError" class="mt-1 text-sm text-red-500">{{ confirmPasswordError }}</p>
          </UFormGroup>
        </div>

        <UButton
          type="submit"
          :color="isFormValid ? 'primary' : 'error'"
          :disabled="!isFormValid"
          :loading="isLoading"
          class="w-full cursor-pointer"
        >
          Завершить регистрацию
        </UButton>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import {useUserStore} from "~/stores/user";

const route = useRoute()
const router = useRouter()

const form = ref({
  inn: '',
  position: '',
  password: '',
  confirmPassword: ''
})

// Password visibility toggles
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Error states for form fields
const innError = ref('')
const positionError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

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

// Validate individual fields and set error messages
const validateInn = () => {
  const result = rules.required(form.value.inn)
  if (result !== true) {
    innError.value = result
    return false
  }

  const innResult = rules.inn(form.value.inn)
  if (innResult !== true) {
    innError.value = innResult
    return false
  }

  innError.value = ''
  return true
}

const validatePosition = () => {
  const result = rules.required(form.value.position)
  if (result !== true) {
    positionError.value = result
    return false
  }

  positionError.value = ''
  return true
}

const validatePassword = () => {
  const result = rules.required(form.value.password)
  if (result !== true) {
    passwordError.value = result
    return false
  }

  const passwordResult = rules.password(form.value.password)
  if (passwordResult !== true) {
    passwordError.value = passwordResult
    return false
  }

  passwordError.value = ''
  // Also validate confirm password when password changes
  if (form.value.confirmPassword) {
    validateConfirmPassword()
  }
  return true
}

const validateConfirmPassword = () => {
  const result = rules.required(form.value.confirmPassword)
  if (result !== true) {
    confirmPasswordError.value = result
    return false
  }

  const confirmResult = rules.confirmPassword(form.value.confirmPassword)
  if (confirmResult !== true) {
    confirmPasswordError.value = confirmResult
    return false
  }

  confirmPasswordError.value = ''
  return true
}

// Run all validations
const validateForm = () => {
  validateInn()
  validatePosition()
  validatePassword()
  validateConfirmPassword()
}
const userStore = useUserStore()

// Computed property for form validity
const isFormValid = computed(() => {
  return !!form.value.inn &&
         !!form.value.position &&
         !!form.value.password &&
         !!form.value.confirmPassword &&
         !innError.value &&
         !positionError.value &&
         !passwordError.value &&
         !confirmPasswordError.value
})

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
  // Validate all fields before submission
  validateForm()

  if (!isFormValid.value) return

  isLoading.value = true
  try {
    // Mock API call to complete registration
    await new Promise(resolve => setTimeout(resolve, 1000))

    // In real app, this would save the data to the database
    // and create the user profile

    const mockResponse = {
      companyName: 'КосмоПорт',
      companyLogo: 'https://sun9-64.userapi.com/impg/IRHOxDleaLUBKmbafJ-j_3Z5Y-pYSMHou64S9A/kASuUQJDYrY.jpg?size=728x546&quality=96&sign=cdbf008a6c9d088a665d8e0b2fb5141a&c_uniq_tag=YJ1-dsBQHtkD4Ssy2wd5CaQpmFxJcQVaq3xbhyqOo38&type=album'
    }

    // Update the store with user data
    userStore.login(mockResponse.companyName, mockResponse.companyLogo)

    // Redirect to profile page with success message
    router.push({
      path: '/profile',
      query: { registered: 'true' }
    })
  } catch (error) {
    console.error('Registration completion error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
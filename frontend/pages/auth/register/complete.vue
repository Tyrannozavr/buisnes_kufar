<script setup lang="ts">
import type {RegisterStep2Data, ApiError} from '~/types/auth'
import {useAuthApi} from '~/api/auth'
import {useUserStore} from "~/stores/user"
import type {CompanyInfo} from "~/types/company";

const route = useRoute()
const router = useRouter()
const authApi = useAuthApi()
const userStore = useUserStore()

const form = ref<RegisterStep2Data>({
  token: '',
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
const isTokenChecking = ref(true)

const rules = {
  required: (value: string) => !!value || 'Обязательное поле',
  inn: (value: string) => {
    if (!value) return true
    return /^\d{10}$/.test(value) || 'ИНН должен содержать 10 цифр'
  },
  password: (value: string) => {
    if (!value) return true
    return value.length >= 8 || 'Пароль должен содержать минимум 8 символов'
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
    console.log('No token provided')
    isTokenValid.value = false
    isTokenChecking.value = false
    return
  }

  // Set token in form
  form.value.token = token

  try {
    console.log('Validating token:', token)
    const response = await authApi.validateRegistrationToken(token)
    console.log('Token validation response:', response)
    isTokenValid.value = response.is_valid
    if (!response.is_valid) {
      console.log('Token is invalid')
      useToast().add({
        title: 'Ошибка',
        description: 'Недействительная ссылка для регистрации',
        color: 'error',
        icon: 'i-heroicons-exclamation-circle'
      })
    }
  } catch (error) {
    console.error('Token validation error:', error)
    isTokenValid.value = false
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось проверить ссылку для регистрации',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
  } finally {
    isTokenChecking.value = false
  }
})

const handleSubmit = async () => {
  try {
    isLoading.value = true
    const response = await authApi.registerStep2(form.value)

    // After successful registration, get company info
    try {
      const companyInfo = await authApi.getCompanyInfo()  as CompanyInfo
      // Update user store with company info
      userStore.login(companyInfo.companyName, companyInfo.companyLogo)
    } catch (error) {
      console.error('Error fetching company info:', error)
      // Continue with redirect even if company info fetch fails
    }

    // Redirect to profile page after successful registration and company info fetch
    router.push('/')
  } catch (error: any) {
    console.error('Registration completion error:', error)
    const errorMessage = error.response?.data?.detail || 'An error occurred during registration'
    useToast().add({
      title: 'Ошибка',
      description: errorMessage,
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900">Завершение регистрации</h2>
        <p class="mt-2 text-sm text-gray-600">Шаг 2 из 2</p>
      </div>

      <!-- Loading state -->
      <div v-if="isTokenChecking" class="flex flex-col items-center justify-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="mt-4 text-gray-600">Проверка ссылки для регистрации...</p>
      </div>

      <!-- Invalid token state -->
      <div v-else-if="!isTokenValid" class="text-center py-8">
        <div class="flex justify-center mb-4">
          <UIcon name="i-heroicons-exclamation-circle" class="h-12 w-12 text-red-500"/>
        </div>
        <p class="text-red-600 mb-4">Недействительная ссылка для регистрации.</p>
        <NuxtLink
            to="/auth/register"
            class="inline-flex items-center text-primary-600 hover:text-primary-500"
        >
          <UIcon name="i-heroicons-arrow-left" class="h-5 w-5 mr-2"/>
          Вернуться к регистрации
        </NuxtLink>
      </div>

      <!-- Registration form -->
      <form v-else class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="flex flex-col space-y-4 w-full">
          <UFormField label="ИНН">
            <UInput
                v-model="form.inn"
                type="text"
                placeholder="Введите ИНН"
                :color="innError ? 'error' : undefined"
                @update:model-value="validateInn"
                class="w-full"
            />
            <p v-if="innError" class="mt-1 text-sm text-red-500">{{ innError }}</p>
          </UFormField>
          <UFormField label="Должность">
            <UInput
                v-model="form.position"
                type="text"
                placeholder="Введите должность"
                :color="positionError ? 'error' : undefined"
                @update:model-value="validatePosition"
                class="w-full"
            />
            <p v-if="positionError" class="mt-1 text-sm text-red-500">{{ positionError }}</p>
          </UFormField>

          <UFormField label="Пароль">
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
          </UFormField>

          <UFormField label="Повторите пароль">
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
          </UFormField>
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


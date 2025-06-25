<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900">Вход в систему</h2>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-4 flex flex-col w-full">
          <UFormField label="ИНН" class="w-full">
            <UInput
              v-model="form.inn"
              type="text"
              placeholder="Введите ИНН"
              :rules="[rules.required, rules.inn]"
              :color="innError ? 'error' : undefined"
              class="w-full"
            />
            <p v-if="innError && form.inn" class="mt-1 text-sm text-red-500">{{ innError }}</p>
          </UFormField>

          <UFormField label="Пароль" class="w-full">
            <UInput
              v-model="form.password"
              type="password"
              placeholder="Введите пароль"
              :rules="[rules.required, rules.password]"
              :color="passwordError ? 'error' : undefined"
              class="w-full"
            />
            <p v-if="passwordError && form.password" class="mt-1 text-sm text-red-500">{{ passwordError }}</p>
          </UFormField>
        </div>

        <div class="text-center">
          <NuxtLink
            to="/auth/recover-password"
            class="text-sm text-primary-600 hover:text-primary-500"
          >
            Восстановить пароль
          </NuxtLink>
        </div>

        <UButton
          type="submit"
          :color="isFormValid ? 'primary' : 'error'"
          :disabled="!isFormValid"
          :loading="isLoading"
          class="w-full cursor-pointer"
        >
          Продолжить
        </UButton>

        <div class="text-center text-sm text-gray-600">
          Для создания аккаунта
          <NuxtLink
            to="/auth/register"
            class="text-primary-600 hover:text-primary-500"
          >
            зарегистрируйтесь
          </NuxtLink>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import { useAuthApi } from '~/api/auth'
import type { CompanyInfo } from '~/types/company'

const form = ref({
  inn: '',
  password: ''
})

const isLoading = ref(false)
const userStore = useUserStore()

const rules = {
  required: (value: string) => !!value || 'Обязательное поле',
  inn: (value: string) => {
    if (!value) return true
    return /^\d{10}$/.test(value) || 'ИНН должен содержать 10 цифр'
  },
  password: (value: string) => {
    if (!value) return true
    return value.length >= 8 || 'Пароль должен содержать минимум 8 символов'
  }
}

const innError = computed(() => {
  if (!form.value.inn) return ''
  const result = rules.inn(form.value.inn)
  return result === true ? '' : result
})

const passwordError = computed(() => {
  if (!form.value.password) return ''
  const result = rules.password(form.value.password)
  return result === true ? '' : result
})

const isFormValid = computed(() => {
  return !!form.value.inn && !!form.value.password &&
    !innError.value && !passwordError.value
})

const handleSubmit = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  try {
    const authApi = useAuthApi()
    
    // Login to get the token
    await authApi.login(form.value.inn, form.value.password)
    
    // Update the store with user data
    await userStore.login()

    // Redirect to profile
    navigateTo("/")
  } catch (error: any) {
    console.error('Login error:', error)
    
    const errorMessage = error.response?._data?.detail || error.detail || error.message
    
    let message = 'Произошла ошибка при входе'
    
    if (errorMessage === 'Incorrect INN or password') {
      message = 'Неверный ИНН или пароль'
    } else if (errorMessage === 'Password must be at least 8 characters long') {
      message = 'Пароль должен содержать минимум 8 символов'
    }
    console.log("Error message:", message)
    // Show error toast with Russian message
    useToast().add({
      title: 'Ошибка',
      description: message,
      icon: 'i-heroicons-exclamation-circle',
      color: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>
<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900">Вход в систему</h2>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-4 flex flex-col w-full">
          <UFormField label="Email или телефон" class="w-full">
            <UInput
              v-model="form.login"
              type="text"
              placeholder="Введите email или номер телефона"
              :rules="[rules.required]"
              :color="loginError ? 'error' : undefined"
              class="w-full"
            />
            <p v-if="loginError && form.login" class="mt-1 text-sm text-red-500">{{ loginError }}</p>
          </UFormField>

          <UFormField label="Пароль" class="w-full">
            <UInput
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Введите пароль"
              :rules="[rules.required, rules.password]"
              :color="passwordError ? 'error' : undefined"
              class="w-full"
            >
              <template #trailing>
                <button
                  type="button"
                  class="cursor-pointer text-gray-400 hover:text-gray-600"
                  :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
                  @click="showPassword = !showPassword"
                >
                  <UIcon
                    :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                    class="h-5 w-5"
                  />
                </button>
              </template>
            </UInput>
            <p v-if="passwordError && form.password" class="mt-1 text-sm text-red-500">{{ passwordError }}</p>
          </UFormField>
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

        <div class="flex items-center justify-between text-sm">
          <NuxtLink
            to="/auth/recover-password"
            class="text-primary-600 hover:text-primary-500"
          >
            Восстановить пароль
          </NuxtLink>
          <NuxtLink
            to="/auth/register"
            class="text-primary-600 hover:text-primary-500"
          >
            Регистрация
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
  login: '',
  password: ''
})

const isLoading = ref(false)
const showPassword = ref(false)
const userStore = useUserStore()

const rules = {
  required: (value: string) => !!value || 'Обязательное поле',
  password: (value: string) => {
    if (!value) return true
    // Для dev-тестов используем короткий пароль (см. ТЗ dimon@gmail.com / 123456)
    return value.length >= 6 || 'Пароль должен содержать минимум 6 символов'
  }
}

const loginError = computed(() => {
  if (!form.value.login) return ''
  return ''
})

const passwordError = computed(() => {
  if (!form.value.password) return ''
  const result = rules.password(form.value.password)
  return result === true ? '' : result
})

const isFormValid = computed(() => {
  return !!form.value.login && !!form.value.password &&
    !loginError.value && !passwordError.value
})

const handleSubmit = async () => {
  if (!isFormValid.value) return

  isLoading.value = true
  try {
    console.log('🔐 Starting login process...')
    console.log('📝 Form data:', { login: form.value.login, password: '***' })
    
    const authApi = useAuthApi()
    
    // Login to get the token
    console.log('🚀 Calling authApi.login...')
    await authApi.login(form.value.login, form.value.password)
    console.log('✅ Login successful, token should be set in cookie')
    
    // Check if token is in cookie
    const accessToken = useCookie('access_token')
    console.log('🍪 Access token in cookie after login:', accessToken.value ? 'Present' : 'Missing')
    if (accessToken.value) {
      console.log('🔍 Token preview:', accessToken.value.substring(0, 20) + '...')
    }
    
    // Add a small delay to ensure cookie is properly set
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Update the store with user data
    console.log('👤 Calling userStore.login() to verify token...')
    await userStore.login()
    console.log('✅ User store updated successfully')

    // Redirect to returnUrl (e.g. /checkout after session expired) or home
    const returnUrl = useRoute().query.returnUrl
    const target = typeof returnUrl === 'string' && returnUrl.startsWith('/') ? returnUrl : '/'
    console.log('🔄 Redirecting to', target)
    navigateTo(target)
  } catch (error: any) {
    console.error('❌ Login error:', error)
    console.error('📊 Error details:', {
      message: error.message,
      status: error.status,
      statusCode: error.statusCode,
      response: error.response?._data,
      data: error.data
    })
    
    const errorMessage = error.response?._data?.detail || error.detail || error.message
    
    let message = 'Произошла ошибка при входе'
    
    if (errorMessage === 'Incorrect INN or password') {
      message = 'Неверный ИНН или пароль'
    } else if (errorMessage === 'Incorrect email/phone or password') {
      message = 'Неверный логин или пароль'
    } else if (errorMessage === 'Password must be at least 6 characters long') {
      message = 'Пароль должен содержать минимум 6 символов'
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
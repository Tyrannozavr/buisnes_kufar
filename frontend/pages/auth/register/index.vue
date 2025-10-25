<script setup lang="ts">
import type {RegisterStep1Data, ApiError} from '~/types/auth'
import {useAuthApi} from '~/api/auth'
import {useRouter} from 'vue-router'

const router = useRouter()
const { $recaptcha } = useNuxtApp()

const form = ref<RegisterStep1Data>({
  firstName: '',
  lastName: '',
  patronymic: '',
  email: '',
  phone: '',
  recaptcha_token: undefined,  // Будет установлен при отправке
  agreement: false
})

// Error states for form fields
const emailError = ref('')
const phoneError = ref('')
const agreementError = ref('')

const isLoading = ref(false)

const rules = {
  required: (value: string | boolean) => {
    if (typeof value === 'boolean') return value || 'Необходимо принять условия'
    return !!value || 'Обязательное поле'
  },
  email: (value: string) => {
    if (!value) return true
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Введите корректный email'
  },
  phone: (value: string) => {
    if (!value) return true
    return /^\+?[0-9]{10,15}$/.test(value) || 'Введите корректный номер телефона'
  }
}

const authApi = useAuthApi()

// Load reCAPTCHA script
onMounted(() => {
  if (typeof window !== 'undefined') {
    const script = document.createElement('script')
    script.src = `https://www.google.com/recaptcha/api.js?render=${($recaptcha as any).siteKey}`
    script.async = true
    script.defer = true
    document.head.appendChild(script)
  }
})

// Validate individual fields and set error messages
const validateEmail = () => {
  const result = rules.required(form.value.email)
  if (result !== true) {
    emailError.value = result
    return false
  }

  const emailResult = rules.email(form.value.email)
  if (emailResult !== true) {
    emailError.value = emailResult
    return false
  }

  emailError.value = ''
  return true
}

const validatePhone = () => {
  const result = rules.required(form.value.phone)
  if (result !== true) {
    phoneError.value = result
    return false
  }

  const phoneResult = rules.phone(form.value.phone)
  if (phoneResult !== true) {
    phoneError.value = phoneResult
    return false
  }

  phoneError.value = ''
  return true
}

const validateAgreement = () => {
  const result = rules.required(form.value.agreement || false)
  if (result !== true) {
    agreementError.value = result
    return false
  }

  agreementError.value = ''
  return true
}

// Run validation on field change
const validateForm = () => {
  validateEmail()
  validatePhone()
  validateAgreement()
}

// Computed property for form validity
const isFormValid = computed(() => {
  return !!form.value.email &&
      !!form.value.phone &&
      form.value.agreement &&
      !emailError.value &&
      !phoneError.value &&
      !agreementError.value
})

const handleSubmit = async () => {
  // Validate all fields before submission
  validateForm()

  if (!isFormValid.value) return

  isLoading.value = true
  try {
    // Execute reCAPTCHA только если не localhost:3000
    const isLocalhost = process.client && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && window.location.port === '3000'
    
    if (isLocalhost) {
      // Для localhost:3000 используем фиктивный токен
      form.value.recaptcha_token = 'localhost-development-token'
    } else {
      // Execute reCAPTCHA для продакшена
      const recaptchaToken = await (($recaptcha as any).execute('register'))
      form.value.recaptcha_token = recaptchaToken
    }

    await authApi.registerStep1(form.value)

    // Reset form after successful registration
    form.value = {
      firstName: '',
      lastName: '',
      patronymic: '',
      email: '',
      phone: '',
      recaptcha_token: undefined,
      agreement: false
    }

    // Show success message
    useToast().add({
      title: 'Успешно',
      description: 'На ваш email отправлена ссылка для завершения регистрации. Пожалуйста, проверьте вашу почту.',
      color: 'success',
      icon: 'i-heroicons-check-circle'
    })

    // Redirect to success page
    await router.push('/auth/register/success')
  } catch (error) {
    const apiError = error as ApiError
    if (apiError.errors) {
      // Display field-specific errors
      Object.entries(apiError.errors).forEach(([field, messages]) => {
        const errorMessage = messages.join(', ')
        switch (field) {
          case 'email':
            emailError.value = errorMessage
            break
          case 'phone':
            phoneError.value = errorMessage
            break
          default:
            useToast().add({
              title: 'Ошибка',
              description: errorMessage,
              color: 'error',
              icon: 'i-heroicons-exclamation-circle'
            })
        }
      })
    } else if (apiError.detail === 'User with this email already exists' || apiError.message === 'User with this email already exists') {
      useToast().add({
        title: 'Информация',
        description: 'На ваш email уже была отправлена ссылка для продолжения регистрации. Пожалуйста, проверьте вашу почту, включая папку "Спам"',
        color: 'info',
        icon: 'i-heroicons-information-circle'
      })
    } else if (apiError.detail && typeof apiError.detail === 'object' && apiError.detail.error_type === 'email_service_unavailable') {
      // Обработка ошибки сервиса email
      useToast().add({
        title: 'Временные трудности',
        description: apiError.detail.message || 'Временные технические трудности с отправкой email. Пожалуйста, попробуйте позже.',
        color: 'warning',
        icon: 'i-heroicons-exclamation-triangle'
      })
      console.error('Email service error:', apiError.detail.verbose_error)
    } else {
      // Display general error message
      useToast().add({
        title: 'Ошибка',
        description: apiError.message || apiError.detail || 'Произошла ошибка при регистрации',
        color: 'error',
        icon: 'i-heroicons-exclamation-circle'
      })
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900">Регистрация</h2>
        <p class="mt-2 text-sm text-gray-600">Шаг 1 из 2</p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="flex flex-col space-y-4 w-full">
          <!-- Name fields split into three separate inputs -->
          <UFormField label="Фамилия (необязательно)">
            <UInput
                v-model="form.lastName"
                type="text"
                placeholder="Введите фамилию"
                class="w-full"
            />
          </UFormField>

          <UFormField label="Имя (необязательно)">
            <UInput
                v-model="form.firstName"
                type="text"
                placeholder="Введите имя"
                class="w-full"
            />
          </UFormField>

          <UFormField label="Отчество (необязательно)">
            <UInput
                v-model="form.patronymic"
                type="text"
                placeholder="Введите отчество"
                class="w-full"
            />
          </UFormField>

          <UFormField label="Email">
            <UInput
                v-model="form.email"
                type="email"
                placeholder="Введите email"
                :color="emailError ? 'error' : undefined"
                @update:model-value="validateEmail"
                class="w-full"
            />
            <p v-if="emailError" class="mt-1 text-sm text-red-500">{{ emailError }}</p>
          </UFormField>

          <UFormField label="Телефон">
            <UInput
                v-model="form.phone"
                type="tel"
                placeholder="Введите номер телефона"
                :color="phoneError ? 'error' : undefined"
                @update:model-value="validatePhone"
                class="w-full"
            />
            <p v-if="phoneError" class="mt-1 text-sm text-red-500">{{ phoneError }}</p>
          </UFormField>

          <div class="flex flex-row">
            <UCheckbox
                v-model="form.agreement"
                :color="agreementError ? 'error' : undefined"
                @update:model-value="validateAgreement"
            />
            <div class="ml-2">
              <p>
                Я принимаю
                <NuxtLink
                    to="/terms"
                    class="text-primary-600 hover:text-primary-500"
                >
                  условия пользовательского соглашения
                </NuxtLink>
              </p>
              <p v-if="agreementError" class="text-sm text-red-500">{{ agreementError }}</p>
            </div>
          </div>
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
          Уже есть аккаунт?
          <NuxtLink
              to="/auth/login"
              class="text-primary-600 hover:text-primary-500"
          >
            Войти
          </NuxtLink>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>

</style>
<script setup lang="ts">
import type {RegisterStep1Data, ApiError} from '~/types/auth'
import {useAuthApi} from '~/api/auth'
import {useRouter} from 'vue-router'

const router = useRouter()
const form = ref<RegisterStep1Data>({
  firstName: '',
  lastName: '',
  patronymic: '',
  email: '',
  phone: '',
  captcha: '',
  agreement: false
})
const isHuman = ref(false)

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

// Handle captcha change
const handleCaptchaChange = (value: boolean | 'indeterminate') => {
  if (value === true) {
    // When checkbox is checked, set a mock captcha value
    form.value.captcha = 'verified'
  } else {
    form.value.captcha = ''
  }
}

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
  const result = rules.required(form.value.agreement)
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
      !!form.value.captcha &&
      form.value.agreement &&
      !emailError.value &&
      !phoneError.value &&
      !agreementError.value
})

const handleSubmit = async () => {
  // Validate all fields before submission
  validateForm()

  if (!isFormValid.value) return
  if (!isHuman.value) {
    useToast().add({
      title: 'Ошибка',
      description: 'Пожалуйста, подтвердите что вы не робот',
      color: 'error',
      icon: 'i-heroicons-exclamation-circle'
    })
    return
  }

  isLoading.value = true
  try {
    console.log('Submitting registration form...')
    await authApi.registerStep1(form.value)
    console.log('Registration successful, redirecting to success page...')
    
    // Reset form after successful registration
    form.value = {
      firstName: '',
      lastName: '',
      patronymic: '',
      email: '',
      phone: '',
      captcha: '',
      agreement: false
    }
    isHuman.value = false

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

          <div class="mt-4 flex items-center">
            <UCheckbox
                v-model="isHuman"
                @update:model-value="handleCaptchaChange"
            />
            <span class="ml-2">Я не робот</span>
          </div>

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
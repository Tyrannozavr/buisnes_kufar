<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-lg">
      <div class="text-center">
        <h2 class="text-3xl font-bold tracking-tight text-gray-900">Вход в систему</h2>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="space-y-4 flex flex-col w-full">
          <UFormGroup label="ИНН" class="w-full">
            <UInput
              v-model="form.inn"
              type="text"
              placeholder="Введите ИНН"
              :rules="[rules.required, rules.inn]"
              :color="innError ? 'error' : undefined"
              class="w-full"
            />
            <p v-if="innError && form.inn" class="mt-1 text-sm text-red-500">{{ innError }}</p>
          </UFormGroup>

          <UFormGroup label="Пароль" class="w-full">
            <UInput
              v-model="form.password"
              type="password"
              placeholder="Введите пароль"
              :rules="[rules.required, rules.password]"
              :color="passwordError ? 'error' : undefined"
              class="w-full"
            />
            <p v-if="passwordError && form.password" class="mt-1 text-sm text-red-500">{{ passwordError }}</p>
          </UFormGroup>
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
import { useRoute } from 'vue-router'

const route = useRoute()
const backUrl = computed(() => {
  return route.query.back_url ? String(route.query.back_url) : '/'
})

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
    return value.length >= 6 || 'Пароль должен содержать минимум 6 символов'
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
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulated API call

    // Mock response - replace with actual API response
    const mockResponse = {
      companyName: 'КосмоПорт',
      companyLogo: 'https://sun9-64.userapi.com/impg/IRHOxDleaLUBKmbafJ-j_3Z5Y-pYSMHou64S9A/kASuUQJDYrY.jpg?size=728x546&quality=96&sign=cdbf008a6c9d088a665d8e0b2fb5141a&c_uniq_tag=YJ1-dsBQHtkD4Ssy2wd5CaQpmFxJcQVaq3xbhyqOo38&type=album'
    }

    // Update the store with user data
    userStore.login(mockResponse.companyName, mockResponse.companyLogo)

    // Redirect to the back_url if available, otherwise to home
    navigateTo(backUrl.value)
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
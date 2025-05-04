<script setup lang="ts">
const form = ref({
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
const captchaError = ref('')

const isLoading = ref(false)
const showModal = ref(false)
const registrationToken = ref('')

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

// Handle captcha change
const handleCaptchaChange = (value: boolean) => {
  if (value) {
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
    alert('Пожалуйста, подтвердите что вы не робот')
    return
  }
  isLoading.value = true
  try {
    // Mock API call to save first step data and generate token
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Generate mock token (in real app this would come from backend)
    registrationToken.value = Math.random().toString(36).substring(2, 15)

    // Show modal with registration link
    showModal.value = true
  } catch (error) {
    console.error('Registration error:', error)
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
          <UFormGroup label="Фамилия (необязательно)">
            <UInput
                v-model="form.lastName"
                type="text"
                placeholder="Введите фамилию"
                class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Имя (необязательно)">
            <UInput
                v-model="form.firstName"
                type="text"
                placeholder="Введите имя"
                class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Отчество (необязательно)">
            <UInput
                v-model="form.patronymic"
                type="text"
                placeholder="Введите отчество"
                class="w-full"
            />
          </UFormGroup>

          <UFormGroup label="Email">
            <UInput
                v-model="form.email"
                type="email"
                placeholder="Введите email"
                :color="emailError ? 'error' : undefined"
                @update:model-value="validateEmail"
                class="w-full"
            />
            <p v-if="emailError" class="mt-1 text-sm text-red-500">{{ emailError }}</p>
          </UFormGroup>

          <UFormGroup label="Телефон">
            <UInput
                v-model="form.phone"
                type="tel"
                placeholder="Введите номер телефона"
                :color="phoneError ? 'error' : undefined"
                @update:model-value="validatePhone"
                class="w-full"
            />
            <p v-if="phoneError" class="mt-1 text-sm text-red-500">{{ phoneError }}</p>
          </UFormGroup>

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

    <!-- Modal for showing registration link -->
    <UModal v-model="showModal">
      <div class="p-4">
        <h3 class="text-lg font-medium text-gray-900">Регистрация успешно начата</h3>
        <p class="mt-2 text-sm text-gray-600">
          Для завершения регистрации перейдите по ссылке:
        </p>
        <div class="mt-4">
          <NuxtLink
              :to="`/auth/register/complete?token=${registrationToken}`"
              class="text-primary-600 hover:text-primary-500 break-all"
          >
            {{ `http://localhost:3000/auth/register/complete?token=${registrationToken}` }}
          </NuxtLink>
        </div>
      </div>
    </UModal>
  </div>
</template>

<style scoped>

</style>
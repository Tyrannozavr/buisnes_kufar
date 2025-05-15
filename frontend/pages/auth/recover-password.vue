<script setup lang="ts">
import { ref } from 'vue'
import { AUTH_API } from '~/api/auth'

interface ApiResponse {
  success: boolean
  message: string
}

const toast = useToast()

const email = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isCodeSent = ref(false)
const isCodeVerified = ref(false)
const isLoading = ref(false)

const showSuccessToast = (message: string) => {
  toast.add({
    title: 'Успешно',
    description: message,
    icon: 'i-lucide-check-circle',
    color: 'success'
  })
}

const showErrorToast = (message: string) => {
  toast.add({
    title: 'Ошибка',
    description: message,
    icon: 'i-lucide-alert-circle',
    color: 'error'
  })
}

const sendCode = async () => {
  try {
    isLoading.value = true
    const response = await $fetch<ApiResponse>(AUTH_API.RECOVER_PASSWORD, {
      method: 'POST',
      body: { email: email.value }
    })
    
    if (response.success) {
      isCodeSent.value = true
      showSuccessToast(response.message)
    }
  } catch (error) {
    showErrorToast('Произошла ошибка при отправке кода')
  } finally {
    isLoading.value = false
  }
}

const verifyCode = async () => {
  if (!code.value) {
    showErrorToast('Введите код подтверждения')
    return
  }

  try {
    isLoading.value = true
    console.log('Sending verification request...')
    const response = await $fetch<ApiResponse>(AUTH_API.VERIFY_CODE, {
      method: 'POST',
      body: { email: email.value, code: code.value }
    })
    
    console.log('Verification response:', response)
    
    if (response.success) {
      isCodeVerified.value = true
      showSuccessToast(response.message)
    } else {
      isCodeVerified.value = false
      showErrorToast(response.message)
      code.value = '' // Очищаем поле с кодом при неверном вводе
    }
  } catch (error) {
    console.error('Verification error:', error)
    showErrorToast('Произошла ошибка при проверке кода')
  } finally {
    isLoading.value = false
  }
}

const resetPassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    showErrorToast('Пароли не совпадают')
    return
  }
  
  try {
    isLoading.value = true
    const response = await $fetch<ApiResponse>(AUTH_API.RESET_PASSWORD, {
      method: 'POST',
      body: {
        email: email.value,
        code: code.value,
        newPassword: newPassword.value
      }
    })
    
    if (response.success) {
      showSuccessToast(response.message)
      // Redirect to login page or handle success
    } else {
      showErrorToast(response.message)
    }
  } catch (error) {
    showErrorToast('Произошла ошибка при сбросе пароля')
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="recover-password">
    <h1>Восстановление пароля</h1>
    
    <form @submit.prevent class="form">
      <div class="form-group">
        <label for="email">Электронная почта</label>
        <input
          id="email"
          v-model="email"
          type="email"
          required
          :disabled="isCodeSent"
        />
        <button
          v-if="!isCodeSent"
          type="button"
          @click="sendCode"
          :disabled="isLoading"
          class="btn btn-primary"
        >
          Получить код
        </button>
      </div>

      <div v-if="isCodeSent" class="form-group">
        <label for="code">Код подтверждения</label>
        <input
          id="code"
          v-model="code"
          type="text"
          required
          :disabled="isCodeVerified"
          placeholder="Введите код из письма"
        />
        <button
          v-if="!isCodeVerified"
          type="button"
          @click="verifyCode"
          :disabled="isLoading"
          class="btn btn-primary"
        >
          {{ isLoading ? 'Проверка...' : 'Подтвердить код' }}
        </button>
      </div>

      <div v-if="isCodeVerified" class="form-group">
        <label for="newPassword">Новый пароль</label>
        <input
          id="newPassword"
          v-model="newPassword"
          type="password"
          required
          placeholder="Введите новый пароль"
        />
      </div>

      <div v-if="isCodeVerified" class="form-group">
        <label for="confirmPassword">Повторите пароль</label>
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          type="password"
          required
          placeholder="Повторите новый пароль"
        />
      </div>

      <button
        v-if="isCodeVerified"
        type="button"
        @click="resetPassword"
        :disabled="isLoading"
        class="btn btn-primary"
      >
        {{ isLoading ? 'Изменение...' : 'Изменить пароль' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
.recover-password {
  max-width: 400px;
  margin: 2rem auto;
  padding: 1rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 500;
}

input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #45a049;
}
</style>
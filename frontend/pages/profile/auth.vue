<script setup lang="ts">
import { ref } from 'vue'

definePageMeta({
  layout: 'profile'
})

const { $api } = useNuxtApp()
const toast = useToast()

// Email change form state
const newEmail = ref('')
const emailPassword = ref('')
const emailCode = ref('')
const isEmailCodeSent = ref(false)
const isEmailCodeVerified = ref(false)
const isEmailLoading = ref(false)

// Password change form state
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isPasswordLoading = ref(false)

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

// Email change handlers
const sendEmailCode = async () => {
  if (!newEmail.value || !emailPassword.value) {
    showErrorToast('Введите новый email и пароль')
    return
  }

  try {
    isEmailLoading.value = true
    const response = await $api.post('/v1/auth/request-email-change', {
      new_email: newEmail.value,
      password: emailPassword.value
    })
    
    if (response.message) {
      isEmailCodeSent.value = true
      showSuccessToast('Код подтверждения отправлен на новый email')
    }
  } catch (error: any) {
    const errorMessage = error.response?._data?.detail || error.response?._data?.message || 'Произошла ошибка при отправке кода'
    showErrorToast(errorMessage)
  } finally {
    isEmailLoading.value = false
  }
}

const verifyEmailCode = async () => {
  if (!emailCode.value) {
    showErrorToast('Введите код подтверждения')
    return
  }

  try {
    isEmailLoading.value = true
    const response = await $api.post('/v1/auth/confirm-email-change', {
      token: emailCode.value
    })
    
    if (response.message) {
      isEmailCodeVerified.value = true
      showSuccessToast('Email успешно изменен')
      // Очищаем поля после успешной смены
      newEmail.value = ''
      emailPassword.value = ''
      emailCode.value = ''
      isEmailCodeSent.value = false
      isEmailCodeVerified.value = false
    }
  } catch (error: any) {
    const errorMessage = error.response?._data?.detail || error.response?._data?.message || 'Произошла ошибка при проверке кода'
    showErrorToast(errorMessage)
    emailCode.value = ''
  } finally {
    isEmailLoading.value = false
  }
}

// Password change handler
const changePassword = async () => {
  if (!oldPassword.value || !newPassword.value || !confirmPassword.value) {
    showErrorToast('Заполните все поля')
    return
  }

  if (newPassword.value !== confirmPassword.value) {
    showErrorToast('Пароли не совпадают')
    return
  }

  try {
    isPasswordLoading.value = true
    const response = await $api.post('/v1/auth/change-password', {
      current_password: oldPassword.value,
      new_password: newPassword.value
    })
    
    if (response.message) {
      showSuccessToast('Пароль успешно изменен')
      // Очищаем поля после успешной смены
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    }
  } catch (error: any) {
    const errorMessage = error.response?._data?.detail || error.response?._data?.message || 'Произошла ошибка при смене пароля'
    showErrorToast(errorMessage)
  } finally {
    isPasswordLoading.value = false
  }
}
</script>

<template>
  <div class="profile-auth">
    <h1>Настройки безопасности</h1>

    <div class="forms-container">
      <!-- Email change form -->
      <div class="form-section">
        <h2>Изменение email</h2>
        <form @submit.prevent class="form">
          <div class="form-group">
            <label for="newEmail">Новый email</label>
            <input
              id="newEmail"
              v-model="newEmail"
              type="email"
              required
              :disabled="isEmailCodeSent"
              placeholder="Введите новый email"
            />
          </div>

          <div class="form-group">
            <label for="emailPassword">Текущий пароль</label>
            <input
              id="emailPassword"
              v-model="emailPassword"
              type="password"
              required
              :disabled="isEmailCodeSent"
              placeholder="Введите текущий пароль"
            />
          </div>

          <div class="form-group">
            <button
              v-if="!isEmailCodeSent"
              type="button"
              @click="sendEmailCode"
              :disabled="isEmailLoading"
              class="btn btn-primary"
            >
              {{ isEmailLoading ? 'Отправка...' : 'Отправить код подтверждения' }}
            </button>
          </div>

          <div v-if="isEmailCodeSent && !isEmailCodeVerified" class="form-group">
            <label for="emailCode">Код подтверждения</label>
            <p class="help-text">Введите 6-значный код, отправленный на новый email</p>
            <input
              id="emailCode"
              v-model="emailCode"
              type="text"
              required
              maxlength="6"
              placeholder="Введите код из письма"
            />
            <button
              type="button"
              @click="verifyEmailCode"
              :disabled="isEmailLoading"
              class="btn btn-primary"
            >
              {{ isEmailLoading ? 'Проверка...' : 'Подтвердить код' }}
            </button>
          </div>

          <div v-if="isEmailCodeVerified" class="success-message">
            <p>✅ Email успешно изменен!</p>
          </div>
        </form>
      </div>

      <!-- Password change form -->
      <div class="form-section">
        <h2>Изменение пароля</h2>
        <form @submit.prevent class="form">
          <div class="form-group">
            <label for="oldPassword">Текущий пароль</label>
            <input
              id="oldPassword"
              v-model="oldPassword"
              type="password"
              required
              placeholder="Введите текущий пароль"
            />
          </div>

          <div class="form-group">
            <label for="newPassword">Новый пароль</label>
            <input
              id="newPassword"
              v-model="newPassword"
              type="password"
              required
              placeholder="Введите новый пароль"
            />
          </div>

          <div class="form-group">
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
            type="button"
            @click="changePassword"
            :disabled="isPasswordLoading"
            class="btn btn-primary"
          >
            {{ isPasswordLoading ? 'Изменение...' : 'Изменить пароль' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-auth {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
}

.forms-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section h2 {
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: #333;
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
  color: #333;
}

input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #4CAF50;
  outline: none;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.btn {
  padding: 0.75rem 1.5rem;
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

h1 {
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.75rem;
}

.help-text {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #c3e6cb;
  margin-top: 1rem;
}

.success-message p {
  margin: 0;
  font-weight: 500;
}
</style> 
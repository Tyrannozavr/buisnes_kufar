<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '~/api/auth'

interface ApiResponse {
  success: boolean
  message: string
}

const toast = useToast()

// Email change form state
const newEmail = ref('')
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
  if (!newEmail.value) {
    showErrorToast('Введите новый email')
    return
  }

  try {
    isEmailLoading.value = true
    const response = await authApi.sendEmailChangeCode(newEmail.value)
    
    if (response.success) {
      isEmailCodeSent.value = true
      showSuccessToast(response.message)
    }
  } catch (error) {
    showErrorToast('Произошла ошибка при отправке кода')
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
    const response = await authApi.changeEmail({
      email: newEmail.value,
      code: emailCode.value
    })
    
    if (response.success) {
      isEmailCodeVerified.value = true
      showSuccessToast(response.message)
      // Очищаем поля после успешной смены
      newEmail.value = ''
      emailCode.value = ''
    } else {
      showErrorToast(response.message)
      emailCode.value = ''
    }
  } catch (error) {
    showErrorToast('Произошла ошибка при проверке кода')
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
    const response = await authApi.changePassword({
      oldPassword: oldPassword.value,
      newPassword: newPassword.value
    })
    
    if (response.success) {
      showSuccessToast(response.message)
      // Очищаем поля после успешной смены
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      showErrorToast(response.message)
    }
  } catch (error) {
    showErrorToast('Произошла ошибка при смене пароля')
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
            <button
              v-if="!isEmailCodeSent"
              type="button"
              @click="sendEmailCode"
              :disabled="isEmailLoading"
              class="btn btn-primary"
            >
              Получить код
            </button>
          </div>

          <div v-if="isEmailCodeSent" class="form-group">
            <label for="emailCode">Код подтверждения</label>
            <input
              id="emailCode"
              v-model="emailCode"
              type="text"
              required
              :disabled="isEmailCodeVerified"
              placeholder="Введите код из письма"
            />
            <button
              v-if="!isEmailCodeVerified"
              type="button"
              @click="verifyEmailCode"
              :disabled="isEmailLoading"
              class="btn btn-primary"
            >
              {{ isEmailLoading ? 'Проверка...' : 'Подтвердить код' }}
            </button>
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
</style> 
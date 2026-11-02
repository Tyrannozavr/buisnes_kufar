<script setup lang="ts">
import { ref, onMounted } from 'vue'

definePageMeta({
  layout: 'profile',
  title: 'Авторизация',
})

const { $api } = useNuxtApp()
const toast = useToast()

const newEmail = ref('')
const emailPassword = ref('')
const emailCode = ref('')
const isEmailCodeSent = ref(false)
const isEmailCodeVerified = ref(false)
const isEmailLoading = ref(false)

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const isPasswordLoading = ref(false)

const emailNotificationsEnabled = ref(false)
const isNotificationsLoading = ref(false)
const isNotificationsSaving = ref(false)

const showSuccessToast = (message: string) => {
  toast.add({
    title: 'Успешно',
    description: message,
    icon: 'i-lucide-check-circle',
    color: 'success',
  })
}

const showErrorToast = (message: string) => {
  toast.add({
    title: 'Ошибка',
    description: message,
    icon: 'i-lucide-alert-circle',
    color: 'error',
  })
}

const sendEmailCode = async () => {
  if (!newEmail.value || !emailPassword.value) {
    showErrorToast('Введите новый email и пароль')
    return
  }

  try {
    isEmailLoading.value = true
    const response = await $api.post('/v1/auth/request-email-change', {
      new_email: newEmail.value,
      password: emailPassword.value,
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
      token: emailCode.value,
    })

    if (response.message) {
      isEmailCodeVerified.value = true
      showSuccessToast('Email успешно изменен')
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

const loadNotificationSettings = async () => {
  try {
    isNotificationsLoading.value = true
    const profile = await $api.get('/v1/auth/me')
    emailNotificationsEnabled.value = profile?.email_notifications_enabled === true
  } catch (error: any) {
    const errorMessage = error.response?._data?.detail || 'Не удалось загрузить настройки уведомлений'
    showErrorToast(errorMessage)
  } finally {
    isNotificationsLoading.value = false
  }
}

const saveNotificationSettings = async () => {
  try {
    isNotificationsSaving.value = true
    await $api.put('/v1/auth/me', {
      email_notifications_enabled: emailNotificationsEnabled.value,
    })
    showSuccessToast(
      emailNotificationsEnabled.value
        ? 'Уведомления на почту включены'
        : 'Уведомления на почту отключены',
    )
  } catch (error: any) {
    const errorMessage = error.response?._data?.detail || 'Не удалось сохранить настройку'
    showErrorToast(errorMessage)
    emailNotificationsEnabled.value = !emailNotificationsEnabled.value
  } finally {
    isNotificationsSaving.value = false
  }
}

onMounted(() => {
  loadNotificationSettings()
})

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
      new_password: newPassword.value,
    })

    if (response.message) {
      showSuccessToast('Пароль успешно изменен')
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
  <div class="max-w-3xl mx-auto">
    <div class="bg-white shadow rounded-lg p-4 space-y-6">
      <h2 class="text-lg font-medium text-gray-900">Авторизация</h2>

      <!-- Уведомления -->
      <section class="space-y-3 border-t border-gray-100 pt-4">
        <h3 class="text-sm font-medium text-gray-900">Уведомления на email</h3>
        <p class="text-sm text-gray-500">
          Дублировать новые сообщения на почту, указанную при регистрации.
          Отключить можно здесь или по ссылке в письме.
        </p>
        <UCheckbox
          v-model="emailNotificationsEnabled"
          label="Получать уведомления о новых сообщениях на email"
          :disabled="isNotificationsLoading || isNotificationsSaving"
          @update:model-value="saveNotificationSettings"
        />
      </section>

      <!-- Email -->
      <section class="space-y-3 border-t border-gray-100 pt-4">
        <h3 class="text-sm font-medium text-gray-900">Изменение email</h3>
        <form class="space-y-3" @submit.prevent>
          <UFormField label="Новый email">
            <UInput
              v-model="newEmail"
              type="email"
              class="w-full"
              placeholder="Введите новый email"
              :disabled="isEmailCodeSent"
            />
          </UFormField>

          <UFormField label="Текущий пароль">
            <UInput
              v-model="emailPassword"
              type="password"
              class="w-full"
              placeholder="Введите текущий пароль"
              :disabled="isEmailCodeSent"
            />
          </UFormField>

          <UButton
            v-if="!isEmailCodeSent"
            color="primary"
            size="sm"
            class="cursor-pointer"
            :loading="isEmailLoading"
            @click="sendEmailCode"
          >
            Отправить код подтверждения
          </UButton>

          <template v-if="isEmailCodeSent && !isEmailCodeVerified">
            <UFormField label="Код подтверждения" hint="6-значный код из письма на новый email">
              <UInput
                v-model="emailCode"
                type="text"
                class="w-full"
                maxlength="6"
                placeholder="Введите код из письма"
              />
            </UFormField>
            <UButton
              color="primary"
              size="sm"
              class="cursor-pointer"
              :loading="isEmailLoading"
              @click="verifyEmailCode"
            >
              Подтвердить код
            </UButton>
          </template>
        </form>
      </section>

      <!-- Пароль -->
      <section class="space-y-3 border-t border-gray-100 pt-4">
        <h3 class="text-sm font-medium text-gray-900">Изменение пароля</h3>
        <form class="space-y-3" @submit.prevent="changePassword">
          <UFormField label="Текущий пароль">
            <UInput
              v-model="oldPassword"
              type="password"
              class="w-full"
              placeholder="Введите текущий пароль"
            />
          </UFormField>

          <UFormField label="Новый пароль">
            <UInput
              v-model="newPassword"
              type="password"
              class="w-full"
              placeholder="Введите новый пароль"
            />
          </UFormField>

          <UFormField label="Повторите пароль">
            <UInput
              v-model="confirmPassword"
              type="password"
              class="w-full"
              placeholder="Повторите новый пароль"
            />
          </UFormField>

          <UButton
            type="submit"
            color="primary"
            size="sm"
            class="cursor-pointer"
            :loading="isPasswordLoading"
          >
            Изменить пароль
          </UButton>
        </form>
      </section>
    </div>
  </div>
</template>

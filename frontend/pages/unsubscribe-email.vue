<script setup lang="ts">
definePageMeta({
  layout: 'default',
})

const route = useRoute()
const { $api } = useNuxtApp()

const status = ref<'loading' | 'success' | 'error'>('loading')
const message = ref('Отключаем уведомления на почту…')

onMounted(async () => {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  if (!token) {
    status.value = 'error'
    message.value = 'Ссылка недействительна: отсутствует токен.'
    return
  }

  try {
    const response = await $api.get('/v1/auth/email-notifications/unsubscribe', {
      params: { token },
    })
    status.value = 'success'
    message.value = response?.message || 'Уведомления на почту отключены.'
  } catch (error: any) {
    status.value = 'error'
    message.value =
      error?.data?.detail ||
      error?.response?._data?.detail ||
      'Не удалось отключить уведомления. Ссылка могла устареть.'
  }
})
</script>

<template>
  <div class="unsubscribe-page">
    <div class="card">
      <h1>Уведомления на email</h1>
      <p :class="status">{{ message }}</p>
      <NuxtLink v-if="status !== 'loading'" to="/profile/auth" class="link">
        Перейти в настройки
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped>
.unsubscribe-page {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.card {
  max-width: 480px;
  width: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  text-align: center;
}

h1 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #222;
}

p {
  color: #444;
  margin-bottom: 1.5rem;
}

p.success {
  color: #155724;
}

p.error {
  color: #842029;
}

.link {
  color: #4caf50;
  text-decoration: underline;
}
</style>

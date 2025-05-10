<script setup lang="ts">
import type {Company} from '~/types/company'
import PageLoader from "~/components/ui/PageLoader.vue";

definePageMeta({
  layout: 'profile'
})

// Get route to check for query parameters
const route = useRoute()

// Check if user just registered
onMounted(() => {
  if (route.query.registered === 'true') {
    // Show success toast for registration
    useToast().add({
      title: 'Успешно',
      description: 'Вы успешно зарегистрировались',
      color: 'success',
      icon: 'i-heroicons-check-circle'
    })

    // Remove the query parameter from URL without reloading the page
    const router = useRouter()
    router.replace({ path: route.path })
  }
})

// Fetch company data using useApi composable
const {
  data: company,
  error: companyError,
  pending: loading,
  refresh: refreshCompany
} = await useApi<Company>('/company/me')


const saving = ref(false)

const handleSaveCompany = async (data: Partial<Company>) => {
  saving.value = true
  try {
    await useApi('/company/me', {
      method: 'PUT',
      body: {...company.value, ...data}
    })
    await refreshCompany()
    useToast().add({
      title: 'Успешно',
      description: 'Данные компании обновлены',
      color: 'primary'
    })
  } catch (e) {
    useToast().add({
      title: 'Ошибка',
      description: e instanceof Error ? e.message : 'Не удалось обновить данные компании',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

</script>

<template>
  <div>
    <div v-if="loading">
      <PageLoader/>
    </div>

    <UAlert
        v-else-if="companyError"
        color="error"
        :title="companyError.toString()"
        icon="i-heroicons-exclamation-circle"
    />

    <UAlert
        v-else-if="!company"
        color="warning"
        title="Данные компании не найдены"
        description="Не удалось загрузить данные компании. Пожалуйста, попробуйте позже."
        icon="i-heroicons-exclamation-triangle"
    />

    <!-- Company Data Section -->
    <CompanyDataForm
        v-else
        :company="company"
        :loading="saving"
        @save="handleSaveCompany"
    />
  </div>
</template>
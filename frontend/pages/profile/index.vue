<script setup lang="ts">
import type {Company} from '~/types/company'
import PageLoader from "~/components/ui/PageLoader.vue";
import { getMyCompany, updateCompany } from '~/api/company'

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

const loading = ref(true)
const company = ref<Company | null>(null)
const companyError = ref<Error | null>(null)

const fetchCompany = async () => {
  loading.value = true
  try {
    company.value = await getMyCompany()
    companyError.value = null
  } catch (error) {
    companyError.value = error instanceof Error ? error : new Error('Failed to fetch company data')
    useToast().add({
      title: 'Ошибка',
      description: companyError.value.message,
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}

// Initial fetch
await fetchCompany()

const saving = ref(false)

const handleSaveCompany = async (data: Partial<Company>) => {
  saving.value = true
  try {
    await updateCompany({...company.value, ...data})
    await fetchCompany()
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
  <div class="max-w-3xl mx-auto">
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
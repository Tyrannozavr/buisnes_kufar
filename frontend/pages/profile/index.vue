<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CompanyResponse, CompanyUpdate } from '~/types/company'
import { getMyCompany, updateCompany, createCompany, uploadCompanyLogo } from '~/api/company'
import { useUserStore } from '~/stores/user'
// Company data
const company = ref<CompanyResponse | null>(null)
const loading = ref(false)
const error = ref<string | undefined>(undefined)
const isNewCompany = ref(false)

const userStore = useUserStore()

definePageMeta({
  layout: 'profile'
})

// Load company data
const loadCompany = async () => {
  loading.value = true
  error.value = undefined
  try {
    company.value = await getMyCompany()
    isNewCompany.value = false
  } catch (e: any) {
    if (e.message === 'COMPANY_NOT_FOUND') {
      // Если компания не найдена, создаем новую
      isNewCompany.value = true
      company.value = {
        id: 0,
        name: '',
        full_name: '',
        slug: '',
        logo: null,
        logo_url: null,
        type: 'company',
        trade_activity: 'Покупатель',
        business_type: 'Производство товаров',
        activity_type: '',
        description: null,
        country: '',
        federal_district: '',
        region: '',
        city: '',
        inn: '',
        ogrn: '',
        kpp: '',
        registration_date: '',
        legal_address: '',
        production_address: null,
        phone: '',
        email: '',
        website: null,
        officials: [],
        total_views: 0,
        monthly_views: 0,
        total_purchases: 0,
        created_at: '',
        updated_at: ''
      }
      return
    }
    error.value = e.message || 'Ошибка загрузки данных компании'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Handle form submission
const handleSave = async (data: CompanyUpdate) => {
  try {
    if (isNewCompany.value) {
      company.value = await createCompany(data)
    } else {
      company.value = await updateCompany(data)
    }
    
    // Update user store with latest company data
    if (company.value) {
      userStore.login(company.value.name, company.value.logo_url || '')
    }
    
    useToast().add({
      title: 'Успешно',
      description: 'Данные компании сохранены',
      color: 'success'
    })
  } catch (error) {
    useToast().add({
      title: 'Ошибка',
      description: 'Не удалось сохранить данные компании',
      color: 'error'
    })
  }
}

// Handle logo upload
const handleLogoUpload = async (file: File) => {
  loading.value = true
  error.value = undefined
  try {
    company.value = await uploadCompanyLogo(file)
    // Update user store with latest company data
    if (company.value) {
      userStore.login(company.value.name, company.value.logo_url || "")
    }
    useToast().add({ title: 'Успешно', description: 'Логотип компании обновлен', color: 'success' })
  } catch (e: any) {
    error.value = e.message || 'Ошибка при загрузке логотипа'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Handle logo update event from form
const handleLogoUpdated = (data: CompanyResponse) => {
  company.value = data
  // Update user store with latest company data
  userStore.login(data.name, data.logo_url || "")
}

// Load company data on mount
onMounted(() => {
  loadCompany()
})
</script>

<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-8">Профиль компании</h1>

    <div v-if="error" class="mb-4 p-4 bg-red-50 text-red-700 rounded-md">
      {{ error }}
    </div>

    <div v-if="loading && !company" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
    </div>

    <CompanyDataForm
      v-else-if="company"
      :company="company"
      :loading="loading"
      :is-new-company="isNewCompany"
      @save="handleSave"
      @logo-upload="handleLogoUpload"
      @logo-updated="handleLogoUpdated"
    />
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CompanyResponse, CompanyUpdate } from '~/types/company'
import { getMyCompany, updateCompany, createCompany, uploadCompanyLogo } from '~/api/company'

// Company data
const company = ref<CompanyResponse | null>(null)
const loading = ref(false)
const error = ref<string | undefined>(undefined)
const isNewCompany = ref(false)

// Load company data
const loadCompany = async () => {
  loading.value = true
  error.value = undefined
  try {
    company.value = await getMyCompany()
    console.log('Company loaded:', company.value)
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
  loading.value = true
  error.value = undefined
  try {
    if (isNewCompany.value) {
      company.value = await createCompany(data)
      useToast().add({ title: 'Успешно', description: 'Компания создана', color: 'success' })
    } else {
      company.value = await updateCompany(data)
      useToast().add({ title: 'Успешно', description: 'Данные компании обновлены', color: 'success' })
    }
  } catch (e: any) {
    error.value = e.message || 'Ошибка при сохранении данных компании'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Handle logo upload
const handleLogoUpload = async (file: File) => {
  loading.value = true
  error.value = undefined
  try {
    company.value = await uploadCompanyLogo(file)
    useToast().add({ title: 'Успешно', description: 'Логотип компании обновлен', color: 'success' })
  } catch (e: any) {
    error.value = e.message || 'Ошибка при загрузке логотипа'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
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
    />
  </div>
</template>
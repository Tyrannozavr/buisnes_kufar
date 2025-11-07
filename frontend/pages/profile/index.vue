<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CompanyResponse, CompanyUpdate } from '~/types/company'
import { getMyCompany, updateCompany, createCompany, uploadCompanyLogo } from '~/api/companyOwner'
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
      userStore.login()
    }
    
    useToast().add({
      title: 'Успешно',
      description: 'Данные компании сохранены',
      color: 'success'
    })
  } catch (error: any) {
    // Обработка ошибок валидации от бэкенда
    let errorMessage = 'Не удалось сохранить данные компании'
    let errorTitle = 'Ошибка'
    
    // Проверяем наличие детализированной информации об ошибке
    if (error.data?.detail) {
      // Обработка ошибок в формате FastAPI/Pydantic
      if (Array.isArray(error.data.detail)) {
        // Форматируем ошибки валидации в человеческий вид
        const validationErrors = error.data.detail.map((err: any) => {
          const field = err.loc?.length > 1 ? err.loc[err.loc.length - 1] : 'неизвестное поле'
          const fieldName = getFieldDisplayName(field)
          const message = err.msg || 'Ошибка валидации'
          return `${fieldName}: ${message}`
        })
        
        errorMessage = validationErrors.join('; ')
        errorTitle = 'Ошибка валидации данных'
      } else if (typeof error.data.detail === 'string') {
        errorMessage = error.data.detail
      }
    } else if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        const validationErrors = error.response.data.detail.map((err: any) => {
          const field = err.loc?.length > 1 ? err.loc[err.loc.length - 1] : 'неизвестное поле'
          const fieldName = getFieldDisplayName(field)
          const message = err.msg || 'Ошибка валидации'
          return `${fieldName}: ${message}`
        })
        
        errorMessage = validationErrors.join('; ')
        errorTitle = 'Ошибка валидации данных'
      } else if (typeof error.response.data.detail === 'string') {
        errorMessage = error.response.data.detail
      }
    }
    
    error.value = errorMessage
    useToast().add({
      title: errorTitle,
      description: errorMessage,
      color: 'error',
      timeout: 8000
    })
  }
}

// Функция для получения человеческого имени поля
const getFieldDisplayName = (field: string): string => {
  const fieldNames: Record<string, string> = {
    'inn': 'ИНН',
    'ogrn': 'ОГРН',
    'kpp': 'КПП',
    'full_name': 'Полное название организации',
    'name': 'Название организации',
    'registration_date': 'Дата регистрации',
    'legal_address': 'Юридический адрес',
    'production_address': 'Адрес производства',
    'phone': 'Телефон',
    'email': 'Email',
    'country': 'Страна',
    'region': 'Регион',
    'city': 'Город',
    'federal_district': 'Федеральный округ',
    'trade_activity': 'Торговая деятельность',
    'business_type': 'Род деятельности',
    'activity_type': 'Вид деятельности',
    'description': 'Описание',
    'website': 'Веб-сайт'
  }
  
  return fieldNames[field] || field
}

// Handle logo upload
const handleLogoUpload = async (file: File) => {
  loading.value = true
  error.value = undefined
  try {
    company.value = await uploadCompanyLogo(file)
    // Update user store with latest company data
    if (company.value) {
      await userStore.login()
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
  userStore.login()
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

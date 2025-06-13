<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Company, CompanyUpdate } from '~/types/company'
import { getMyCompany, updateCompany, uploadCompanyLogo } from '~/api/company'

// Company data
const company = ref<Company | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

// Load company data
const loadCompany = async () => {
  loading.value = true
  error.value = null
  try {
    company.value = await getMyCompany()
  } catch (e: any) {
    error.value = e.message || 'Ошибка загрузки данных компании'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Handle form submission
const handleSave = async (data: CompanyUpdate) => {
  loading.value = true
  error.value = null
  try {
    company.value = await updateCompany(data)
    useToast().add({ title: 'Успешно', description: 'Данные компании обновлены', color: 'success' })
  } catch (e: any) {
    error.value = e.message || 'Ошибка при обновлении данных компании'
    useToast().add({ title: 'Ошибка', description: error.value, color: 'error' })
  } finally {
    loading.value = false
  }
}

// Handle logo upload
const handleLogoUpload = async (file: File) => {
  loading.value = true
  error.value = null
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
    <h1 class="text-2xl font-bold text-gray-900 mb-8">Company Profile</h1>

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
      @save="handleSave"
      @logo-upload="handleLogoUpload"
    />
  </div>
</template>
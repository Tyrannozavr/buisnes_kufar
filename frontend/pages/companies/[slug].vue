<script setup lang="ts">
import type {CompanyDetails} from '~/types/company'
//
import {getCompany, getCompanyProductsPaginated, getCompanyStatistics} from '~/api/company'
import CompanyProductsPublic from "~/components/products/CompanyProductsPublic.vue";
import { useUserStore } from '~/stores/user'
import { navigateToChatBySlug, createChatForCompany } from '~/composables/chat'
//
// const { createChat } = useChatsApi()
// // Get company ID from route
const route = useRoute()
const companySlug = route.params.slug as string
const userStore = useUserStore()

// Pagination state
const currentPage = ref(1)
const perPage = 12

// Watch for page changes
watch(currentPage, async (newPage) => {
  await refreshProducts()
})

// Fetch company data
const {data: company, error: companyError} = await getCompany(companySlug)

// Fetch company products with pagination
const {data: productsResponse, refresh: refreshProducts} = await getCompanyProductsPaginated(companySlug, currentPage.value, perPage)

// Fetch company statistics
const {data: statistics} = await getCompanyStatistics(companySlug)

// Автоматически создаем чат при переходе на страницу компании (если пользователь авторизован и это не его компания)
if (userStore.isAuthenticated && company.value && company.value.slug !== userStore.companySlug) {
  try {
    await createChatForCompany(
      company.value.slug,
      company.value.name,
      company.value.logo_url || undefined
    )
  } catch (error) {
    console.error('Failed to create chat:', error)
  }
}

//
// Prepare company details
const companyDetails = computed(() => (
    {
      id: company.value?.id || 0,
      logo_url: company.value?.logo_url || null,
      description: company.value?.description || '',
      inn: company.value?.inn ?? '',
      ogrn: company.value?.ogrn ?? '',
      ogrnDate: company.value?.registration_date ?? '',
      registrationDate: company.value?.registration_date ?? '',
      kpp: company.value?.kpp ?? '',
      legalAddress: company.value?.legal_address ?? '',
      productionAddress: company.value?.production_address ?? '',
      phone: company.value?.phone ?? '',
      email: company.value?.email ?? '',
      website: company.value?.website ?? ''
    }
))

// Проверяем, что пользователь не смотрит на свою компанию
const isOwnCompany = computed(() => {
  if (!userStore.isAuthenticated || !company.value) return false
  // Сравниваем по slug или по названию компании
  return company.value.slug === userStore.companySlug || 
         company.value.name === userStore.companyName
})

// // Handle chat creation
const handleCreateChat = async () => {
  await navigateToChatBySlug(companySlug)
}

// Handle page change
const handlePageChange = (page: number) => {
  currentPage.value = page
}

</script>

<template>
  <div class="company-page py-6">
    <UContainer>
      <!-- Заголовок -->
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-3xl font-bold">{{ company?.name }}</h1>
        <UButton
            v-if="company && !isOwnCompany && userStore.isAuthenticated"
            color="primary"
            @click="handleCreateChat"
        >
          Написать сообщение
        </UButton>
      </div>

      <!-- Основная информация -->
      <CompanyDetails
          v-if="companyDetails"
          v-bind="companyDetails"
      />

      <!-- Статистика -->
      <CompanyStatistics
          v-if="statistics"
          v-bind="statistics"
      />

      <!-- Продукция -->
      <h2 class="text-2xl font-bold mb-4 mt-8">Продукция компании</h2>
      <CompanyProductsPublic
          class="mt-6"
          :products="productsResponse?.products || []"
      />

      <!-- Пагинация -->
      <div v-if="productsResponse && productsResponse.total > perPage" class="mt-6 flex justify-center">
        <UPagination
            v-model="currentPage"
            :total="productsResponse.total"
            :page-count="Math.ceil(productsResponse.total / perPage)"
            :per-page="perPage"
            @update:model-value="handlePageChange"
        />
      </div>
    </UContainer>
  </div>
</template>
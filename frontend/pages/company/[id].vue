<script setup lang="ts">
import type {CompanyDetails} from '~/types/company'
import { useChatsApi } from '~/api/chats'

import { getCompany, getCompanyProducts, getCompanyStatistics } from '~/api/company'

const { createChat } = useChatsApi()
// Get company ID from route
const route = useRoute()
const companyId = route.params.id as string

// Fetch company data
const {data: company} = await getCompany(companyId)

// Fetch company products
const {data: products} = await getCompanyProducts(companyId)

// Fetch company statistics
const {data: statistics} = await getCompanyStatistics(companyId)

// Prepare company details
const companyDetails = computed<CompanyDetails>(() => ({
  description: company?.description ?? '',
  inn: company?.inn ?? '',
  ogrn: company?.ogrn ?? '',
  ogrnDate: company?.registration_date ?? '',
  kpp: company?.kpp ?? '',
  legalAddress: company?.legal_address ?? '',
  productionAddress: company?.production_address ?? '',
  phone: company?.phone ?? '',
  email: company?.email ?? '',
  website: company?.website ?? ''
}))

// Handle chat creation
const handleCreateChat = async () => {
  const { chat_id } = await createChat(company.id)
  console.log(chat_id)

  if (chat_id) {
    navigateTo(`/profile/messages/${chat_id}`)
  }
}
</script>

<template>
  <div class="company-page py-6">
    <UContainer>
      <!-- Заголовок -->
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-3xl font-bold">{{ company?.name }}</h1>
        <UButton
          v-if="company"
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
      <CompanyProducts
          class="mt-6"
          mode="client"
          :products="products || []"
      />
    </UContainer>
  </div>
</template>
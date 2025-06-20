<script setup lang="ts">
import type {CompanyDetails, CompanyResponse} from '~/types/company'
//
import { getCompany, getCompanyProducts, getCompanyStatistics } from '~/api/company'
import {navigateToChatById} from "~/composables/chat";
//
// const { createChat } = useChatsApi()
// // Get company ID from route
const route = useRoute()
const companySlug = route.params.slug as string
//
// // Fetch company data
const { data: company } = await getCompany(companySlug) as { data: Ref<CompanyResponse | null> }//
// Fetch company products
const {data: products} = await getCompanyProducts(companySlug)
//
// Fetch company statistics
const {data: statistics} = await getCompanyStatistics(companySlug)
//
// Prepare company details
const companyDetails = computed<CompanyDetails>(() => (
    {
      description: company.value?.description,
      inn: company.value?.inn ?? '',
      ogrn: company.value?.ogrn ?? '',
      ogrnDate: company.value?.registration_date ?? '',
      kpp: company.value?.kpp ?? '',
      legalAddress: company.value?.legal_address ?? '',
      productionAddress: company.value?.production_address ?? '',
      phone: company.value?.phone ?? '',
      email: company.value?.email ?? '',
      website: company.value?.website ?? ''
    }
))

// // Handle chat creation
const handleCreateChat = async () => {
  await navigateToChatBySlug(companySlug)
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
      {{products}}
    </UContainer>
  </div>
</template>
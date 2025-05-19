<script setup lang="ts">
import type {CompanyDetails} from '~/types/company'

import { getCompany, getCompanyProducts, getCompanyStatistics } from '~/api/company'
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
  description: company.value?.description ?? '',
  inn: company.value?.inn ?? '',
  ogrn: company.value?.ogrn ?? '',
  ogrnDate: company.value?.registrationDate ?? '',
  kpp: company.value?.kpp ?? '',
  legalAddress: company.value?.legalAddress ?? '',
  productionAddress: company.value?.productionAddress ?? '',
  phone: company.value?.phone ?? '',
  email: company.value?.email ?? '',
  website: company.value?.website ?? ''
}))

</script>

<template>
  <div class="company-page py-6">
    <UContainer>
      <!-- Заголовок -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold">{{ company?.name }}</h1>
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
      <CompanyProducts
          :products="products || []"
      />
    </UContainer>
  </div>
</template>
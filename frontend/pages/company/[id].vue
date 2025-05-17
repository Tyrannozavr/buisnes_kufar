<script setup lang="ts">
import type { Company, CompanyDetails, CompanyStatistics } from '~/types/company'
import type { Product } from '~/types/product'
import type { Review } from '~/types/review'

// Get company ID from route
const route = useRoute()
const companyId = route.params.id as string

// Fetch company data
const { data: company } = await useApi<Company>(`/companies/${companyId}`)

// Fetch company products
const { data: products } = await useApi<Product[]>(`/companies/${companyId}/products`)

// Fetch company reviews
const { data: reviews } = await useApi<Review[]>(`/companies/${companyId}/reviews`)

// Fetch company statistics
const { data: statistics } = await useApi<CompanyStatistics>(`/companies/${companyId}/statistics`)

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

// Вычисляемые свойства для статистики
const totalProducts = computed(() => products.value?.length ?? 0)
const totalReviews = computed(() => reviews.value?.length ?? 0)
const averageRating = computed(() => {
  if (!reviews.value?.length) return 0
  const sum = reviews.value.reduce((acc: number, review: Review) => acc + review.rating, 0)
  return sum / reviews.value.length
})

// Моковые данные для просмотров
const totalViews = ref(1234)
const monthlyViews = ref(123)
</script>

<template>
  <div class="company-page py-6">
    <UContainer>
      <!-- Заголовок -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold">{{ company?.name }}</h1>
        <UButton
          v-if="company?.isOwner"
          color="primary"
          to="/company/edit"
        >
          Редактировать
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
      <CompanyProducts
        :products="products ?? []"
      />
      
      <!-- Отзывы -->
      <CompanyReviews
        :reviews="reviews ?? []"
      />
    </UContainer>
  </div>
</template>

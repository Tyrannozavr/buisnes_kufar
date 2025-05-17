<script setup lang="ts">
import type {CompanyDetails, CompanyStatistics} from '~/types/company'
import type {Review} from '~/types/review'
import {useReviewsApi} from '~/api/reviews'

// Get company ID from route
const route = useRoute()
const companyId = route.params.id as string

// Use company API composable
const {getCompany, getCompanyProducts, getCompanyReviews, getCompanyStatistics} = useCompanyApi()
const {submitReview} = useReviewsApi()

// Fetch company data
const {data: company} = await getCompany(companyId)

// Fetch company products
const {data: products} = await getCompanyProducts(companyId)

// Fetch company reviews
// const {data: reviews} = await getCompanyReviews(companyId)

// Fetch company statistics
const {data: statistics} = await getCompanyStatistics(companyId)

// // Handle review submission
// const handleSubmitReview = async (reviewData: { rating: number; text: string }) => {
//   const {data: newReview} = await submitReview(companyId, reviewData)
//   if (newReview.value) {
//     // Refresh reviews after successful submission
//     const {data: updatedReviews} = await getCompanyReviews(companyId)
//     if (updatedReviews.value) {
//       reviews.value = updatedReviews.value
//     }
//   }
// }

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
<!--      <CompanyReviews-->
<!--          :reviews="reviews ?? []"-->
<!--          @submit-review="handleSubmitReview"-->
<!--      />-->
    </UContainer>
  </div>
</template>

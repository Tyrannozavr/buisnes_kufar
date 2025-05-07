<script setup lang="ts">
import type { Product } from '~/types/product'
import type { Company } from '~/types/company'
import PageLoader from "~/components/ui/PageLoader.vue";
import ProductCard from "~/components/company/ProductCard.vue";

// Fetch products and companies data using the useApi composable
const { data: products, error: productsError, pending: productsPending } = await useApi<Product[]>('/products')
const { data: companies, error: companiesError, pending: companiesPending } = await useApi<Company[]>('/companies')

// Derive countries, regions, and cities from the API data
const countries = computed(() => {
  if (!companies.value) return []
  return [...new Set((companies.value as Company[]).map(company => company.country))].sort()
})

const regions = computed(() => {
  if (!companies.value) return []
  return [...new Set((companies.value as Company[]).map(company => company.region))].sort()
})

const cities = computed(() => {
  if (!companies.value) return []
  return [...new Set((companies.value as Company[]).map(company => company.city))].sort()
})

// Search state
const search = ref({
  name: '',
  country: '',
  region: '',
  city: ''
})

// Filtered services (products with type 'service')
const filteredServices = computed(() => {
  if (!products.value || !companies.value) return []

  return (products.value as Product[])
      .filter(product => product.type === 'service')
      .filter(product => {
        const company = (companies.value as Company[]).find(c => c.id === product.companyId)
        if (!company) return false

        const matchesName = !search.value.name ||
            product.name.toLowerCase().includes(search.value.name.toLowerCase())

        const matchesCountry = !search.value.country ||
            company.country === search.value.country

        const matchesRegion = !search.value.region ||
            company.region === search.value.region

        const matchesCity = !search.value.city ||
            company.city === search.value.city

        return matchesName && matchesCountry && matchesRegion && matchesCity
      })
})

// Handle add to cart or contact
const handleContact = (product: Product) => {
  // TODO: Implement contact functionality
  console.log('Contact about service:', product)
}
</script>

<template>
  <div class="space-y-8">
    <!-- Search and Filters -->
    <section class="bg-white rounded-lg p-6 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <UFormGroup label="Название">
          <UInput
              v-model="search.name"
              placeholder="Поиск по названию"
          />
        </UFormGroup>

        <UFormGroup label="Страна">
          <USelect
              v-model="search.country"
              :options="countries"
              placeholder="Выберите страну"
          />
        </UFormGroup>

        <UFormGroup label="Федеральный округ">
          <USelect
              v-model="search.region"
              :options="regions"
              placeholder="Выберите округ"
              :disabled="!search.country || search.country !== 'Россия'"
          />
        </UFormGroup>

        <UFormGroup label="Регион">
          <USelect
              v-model="search.city"
              :options="cities"
              placeholder="Выберите регион"
          />
        </UFormGroup>
      </div>
    </section>

    <!-- Loading state -->
    <section v-if="productsPending || companiesPending" class="bg-white rounded-lg p-6 shadow-sm">
      <PageLoader class="mx-auto" />
      <p class="text-center mt-4 text-gray-500">Загрузка услуг...</p>
    </section>

    <!-- Error state -->
    <section v-else-if="productsError || companiesError" class="bg-white rounded-lg p-6 shadow-sm">
      <p class="text-red-500 text-center">
        Произошла ошибка при загрузке данных. Пожалуйста, попробуйте позже.
      </p>
    </section>

    <!-- Empty state -->
    <section v-else-if="filteredServices.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
      <p class="text-center text-gray-500">
        {{ products && products.length > 0 ? 'Нет услуг, соответствующих критериям поиска' : 'Нет доступных услуг' }}
      </p>
    </section>

    <!-- Services Grid -->
    <section v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <ProductCard
            v-for="service in filteredServices"
            :key="service.id"
            :product="service"
            @add-to-cart="handleContact"
            button-text="Связаться"
        />
      </div>
    </section>
  </div>
</template>
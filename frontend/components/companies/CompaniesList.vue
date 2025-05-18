<script setup lang="ts">
import type {CompanyShort} from '~/types/company'
import PageLoader from "~/components/ui/PageLoader.vue";
import CompanyCard from "~/components/companies/CompanyCard.vue";

const props = defineProps<{
  manufacturers: CompanyShort[]
  pending: boolean
  error: Error | null
}>()

console.log('CompaniesList props:', {
  manufacturers: props.manufacturers,
  pending: props.pending,
  error: props.error
})
</script>

<template>
  <!-- Loading state -->
  <section v-if="pending" class="bg-white rounded-lg p-6 shadow-sm">
    <PageLoader text="Загрузка данных о производителях..." class="mx-auto" />
  </section>

  <!-- Error state -->
  <UAlert v-else-if="error" color="error" variant="soft" class="mb-4">
    Не удалось загрузить данные о производителях
  </UAlert>

  <!-- Empty state -->
  <section v-else-if="manufacturers.length === 0" class="bg-white rounded-lg p-6 shadow-sm">
    <p class="text-center text-gray-500">
      Нет производителей, соответствующих критериям поиска
    </p>
  </section>
  <!-- Manufacturers List -->
  <div v-else class="space-y-4">
    <CompanyCard
      v-for="manufacturer in manufacturers"
      :key="manufacturer.id"
      :manufacturer="manufacturer"
    />
  </div>
</template> 
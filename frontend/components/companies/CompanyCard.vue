<script setup lang="ts">
import type {CompanyShort} from '~/types/company'
import { useCompaniesApi } from '~/api/companies'

const props = defineProps<{
  manufacturer: CompanyShort
}>()

const router = useRouter()
const { deletePartnerById } = useCompaniesApi()

// const handleDelete = async () => {
//   try {
//     await deletePartnerById(props.manufacturer.id)
//     useToast().add({
//       title: 'Успешно',
//       description: 'Компания удалена',
//       color: 'success'
//     })
//   } catch (error) {
//     useToast().add({
//       title: 'Ошибка',
//       description: 'Не удалось удалить компанию',
//       color: 'error'
//     })
//   }
// }
</script>

<template>
  <UCard class="hover:shadow-lg transition-shadow">
    <div class="flex items-start gap-4">
      <!-- Logo -->
      <NuxtLink
          :to="`/companies/${manufacturer.slug}`"
          class="w-24 h-24 flex-shrink-0">
        <NuxtImg
          :src="manufacturer.logo_url || undefined"
          :alt="manufacturer.name"
          class="w-full h-full object-cover rounded-lg"
        />
      </NuxtLink>

      <!-- Info -->
      <div class="flex-grow">
        <div class="flex justify-between items-start">
          <div>
            <NuxtLink
                :to="`/companies/${manufacturer.slug}`"
                class="text-lg font-medium">{{ manufacturer.name }}</NuxtLink>
            <p class="text-gray-600">{{ manufacturer.description }}</p>
          </div>
          <div class="flex gap-2">
            <MessageButton
              :company-id="manufacturer.id"
              :company-name="manufacturer.name"
              color="primary"
              variant="soft"
              size="md"
              custom-text="Написать сообщение"
            />
<!--            <UButton-->
<!--              color="error"-->
<!--              variant="soft"-->
<!--              class="cursor-pointer"-->
<!--              @click="handleDelete"-->
<!--            >-->
<!--              Удалить-->
<!--            </UButton>-->
          </div>
        </div>

        <!-- Location -->
        <div class="mt-2 text-sm text-gray-500">
          {{ manufacturer.city }}, {{ manufacturer.region }}, {{ manufacturer.country }}
        </div>

      </div>
    </div>
  </UCard>
</template>
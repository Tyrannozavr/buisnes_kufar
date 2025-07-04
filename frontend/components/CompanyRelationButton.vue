<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '~/stores/user'
import { addCompanyRelation, removeCompanyRelation, getCompanyRelations } from '~/api/company'
import { CompanyRelationType } from '~/types/company'
import { useToast } from 'vue-toastification'

interface Props {
  companyId: number
  companyName?: string
  companySlug?: string
}

const props = defineProps<Props>()
const userStore = useUserStore()
const toast = useToast()

const isOwnCompany = computed(() => {
  if (!userStore.isAuthenticated) return false
  return props.companyId === userStore.companyId
})

const relations = ref<{ [key in CompanyRelationType]?: boolean }>({})
const loading = ref(false)

const fetchRelations = async () => {
  if (!userStore.isAuthenticated || isOwnCompany.value) return
  loading.value = true
  try {
    for (const type of Object.values(CompanyRelationType)) {
      const { data } = await getCompanyRelations(type as CompanyRelationType)
      const relationsArr = data?.data ?? data ?? []
      relations.value[type as CompanyRelationType] = Array.isArray(relationsArr)
        ? relationsArr.some((rel: any) => rel.related_company_id === props.companyId)
        : false
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchRelations)

const handleAdd = async (type: CompanyRelationType) => {
  loading.value = true
  try {
    await addCompanyRelation(props.companyId, type)
    relations.value[type] = true
    toast.success('Компания добавлена в список')
  } catch (e) {
    toast.error('Ошибка при добавлении')
  } finally {
    loading.value = false
  }
}

const handleRemove = async (type: CompanyRelationType) => {
  loading.value = true
  try {
    await removeCompanyRelation(props.companyId, type)
    relations.value[type] = false
    toast.success('Компания удалена из списка')
  } catch (e) {
    toast.error('Ошибка при удалении')
  } finally {
    loading.value = false
  }
}

function relationLabel(type: CompanyRelationType) {
  switch (type) {
    case CompanyRelationType.PARTNER:
      return 'партнеров'
    case CompanyRelationType.SUPPLIER:
      return 'поставщиков'
    case CompanyRelationType.BUYER:
      return 'покупателей'
    default:
      return ''
  }
}
</script>

<template>
  <div v-if="userStore.isAuthenticated && !isOwnCompany">
    <div class="flex gap-2">
      <template v-for="type in [CompanyRelationType.PARTNER, CompanyRelationType.SUPPLIER, CompanyRelationType.BUYER]" :key="type">
        <UButton
          :loading="loading"
          :color="relations[type] ? 'success' : 'primary'"
          :variant="relations[type] ? 'soft' : 'solid'"
          size="md"
          class="min-w-[180px]"
          @click="relations[type] ? handleRemove(type) : handleAdd(type)"
        >
          {{ relations[type] ? `Удалить из ${relationLabel(type)}` : `Добавить в ${relationLabel(type)}` }}
        </UButton>
      </template>
    </div>
  </div>
</template>

<style scoped>
.flex {
  display: flex;
  gap: 0.5rem;
}
.min-w-180px {
  min-width: 180px;
}
</style> 
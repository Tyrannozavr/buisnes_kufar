<script setup lang="ts">
import { getCompanyRelations, addCounterparty, removeCounterparty } from '~/api/company'
import { CompanyRelationType, isLogisticsTradeActivity, type TradeActivity } from '~/types/company'
import { useUserStore } from '~/stores/user'
import { getMyCompany } from '~/api/companyOwner'

interface Props {
  companyId: number
  companyName?: string
  companySlug?: string
  /** Торговая деятельность компании на странице (целевая) */
  targetTradeActivity?: string | null
}

const props = defineProps<Props>()
const userStore = useUserStore()
const toast = useToast()

const isOwnCompany = computed(() => {
  if (!userStore.isAuthenticated) return false
  return props.companyId === userStore.companyId
})

const viewerIsLogistics = ref(false)
const linked = ref(false)
const loading = ref(false)
const dialogOpen = ref(false)
const asSupplier = ref(false)
const asBuyer = ref(true)

const targetIsLogistics = computed(() =>
  isLogisticsTradeActivity(props.targetTradeActivity as TradeActivity | null | undefined),
)

onMounted(async () => {
  if (!userStore.isAuthenticated || isOwnCompany.value) return
  try {
    const me = await getMyCompany()
    viewerIsLogistics.value = isLogisticsTradeActivity(me?.trade_activity)
  } catch {
    viewerIsLogistics.value = false
  }
  await fetchLinked()
})

const fetchLinked = async () => {
  loading.value = true
  try {
    const { data } = await getCompanyRelations()
    const relationsArr = (data?.data ?? data ?? []) as { related_company_id: number }[]
    linked.value = Array.isArray(relationsArr)
      ? relationsArr.some((rel) => rel.related_company_id === props.companyId)
      : false
  } finally {
    loading.value = false
  }
}

const onPrimaryClick = async () => {
  if (linked.value) {
    await handleRemove()
    return
  }
  // Целевая — перевозчик/экспедитор: сразу в Контрагенты + Перевозчики
  if (targetIsLogistics.value) {
    await doAdd({ asCarrier: true })
    return
  }
  // Продавец/производитель: диалог ролей (у логистики-viewer без supplier/buyer — только контрагент)
  if (viewerIsLogistics.value) {
    await doAdd({})
    return
  }
  dialogOpen.value = true
  asSupplier.value = false
  asBuyer.value = true
}

const confirmDialog = async () => {
  if (!asSupplier.value && !asBuyer.value) {
    toast.add({
      title: 'Выберите роль',
      description: 'Отметьте «Поставщики» и/или «Покупатели»',
      color: 'warning',
    })
    return
  }
  dialogOpen.value = false
  await doAdd({ asSupplier: asSupplier.value, asBuyer: asBuyer.value })
}

const doAdd = async (opts: { asSupplier?: boolean; asBuyer?: boolean; asCarrier?: boolean }) => {
  loading.value = true
  try {
    await addCounterparty(props.companyId, opts)
    linked.value = true
    toast.add({ title: 'Контрагент добавлен', color: 'success' })
  } catch {
    toast.add({ title: 'Не удалось добавить контрагента', color: 'error' })
  } finally {
    loading.value = false
  }
}

const handleRemove = async () => {
  loading.value = true
  try {
    await removeCounterparty(props.companyId)
    linked.value = false
    toast.add({ title: 'Контрагент удалён из списков', color: 'success' })
  } catch {
    toast.add({ title: 'Ошибка при удалении', color: 'error' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="userStore.isAuthenticated && !isOwnCompany">
    <UButton
      :loading="loading"
      :color="linked ? 'success' : 'primary'"
      :variant="linked ? 'soft' : 'solid'"
      size="md"
      class="min-w-[200px]"
      @click="onPrimaryClick"
    >
      {{ linked ? 'Удалить контрагента' : 'Добавить контрагента' }}
    </UButton>

    <UModal v-model:open="dialogOpen" title="Добавить контрагента">
      <template #body>
        <div class="flex flex-col gap-3">
          <p class="text-sm text-neutral-600">
            Компания попадёт в «Контрагенты». Выберите также списки:
          </p>
          <UCheckbox v-model="asSupplier" label="Поставщики" />
          <UCheckbox v-model="asBuyer" label="Покупатели" />
          <div class="flex gap-2 mt-2">
            <UButton label="Отмена" color="neutral" variant="subtle" class="flex-1" @click="dialogOpen = false" />
            <UButton label="Добавить" color="primary" class="flex-1" :loading="loading" @click="confirmDialog" />
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>

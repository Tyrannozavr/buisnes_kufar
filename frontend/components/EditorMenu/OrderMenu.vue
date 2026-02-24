<template>
	<div class="flex flex-col gap-2">
		<UButton label="СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="createBill()" />
		<UButton label="ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="createSupplyContract()" />
    <UButton label="ДОГОВОР на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
      :disabled="activeButtons" @click="createContract()" />
		<UButton label="Сопроводительные документы на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="activeButtons" @click="inDevelopment()" />
	</div>
</template>

<script setup lang="ts">
import { usePurchasesApi } from '~/api/purchases';
import { useRoute, useRouter } from 'vue-router';
import { Editor } from '~/constants/keys';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';

const route = useRoute()
const router = useRouter()
const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const { createBill: createBillApi, createSupplyContract: createSupplyContractApi, createContract: createContractApi } = usePurchasesApi()
const activeTab = useTypedState(Editor.ACTIVE_TAB)

defineProps<{
	activeButtons: boolean
	inDevelopment: () => any
}>()

function formatSupplyContractDate (value: string | unknown): string {
  if (typeof value === 'string') return value
  if (value && typeof value === 'object' && 'toString' in value) return String(value)
  return ''
}

const createBill = async () => {
  const response = await createBillApi(Number(route.query.dealId))
  activeTab.value = '1'
  router.replace({...route, hash: '#bill'})
}

const createSupplyContract = async () => {
  const dealId = Number(route.query.dealId)
  const role = String(route.query.role ?? '')
  const productType = String(route.query.productType ?? 'goods')
  const response = await createSupplyContractApi(dealId)
  if (response?.supply_contracts_number != null) {
    const payload = {
      supplyContractNumber: String(response.supply_contracts_number),
      supplyContractDate: formatSupplyContractDate(response.supply_contracts_date ?? ''),
    }
    if (role === 'buyer') {
      purchasesStore.updateDealSupplyContract(dealId, productType, payload)
    } else {
      salesStore.updateDealSupplyContract(dealId, productType, payload)
    }
  }
  activeTab.value = '2'
  router.replace({...route, hash: '#supplyContract'})
}

const createContract = async () => {
  const response = await createContractApi(Number(route.query.dealId))
  console.log('createContract:', response)
  activeTab.value = '3'
  router.replace({...route, hash: '#contract'})
}
</script>

<style scoped></style>
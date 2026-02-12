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

const route = useRoute()
const router = useRouter()
const { createBill: createBillApi, createSupplyContract: createSupplyContractApi, createContract: createContractApi } = usePurchasesApi()
const activeTab = useTypedState(Editor.ACTIVE_TAB)

defineProps<{
	activeButtons: boolean
	inDevelopment: () => any
}>()

const createBill = async () => {
  const response = await createBillApi(Number(route.query.dealId))
  console.log('createBill:', response)
  activeTab.value = '1'
  router.replace({...route, hash: '#bill'})
}

const createSupplyContract = async () => {
  const response = await createSupplyContractApi(Number(route.query.dealId))
  console.log('createSupplyContract:', response)
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
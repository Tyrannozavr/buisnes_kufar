<template>
	<div class="flex flex-col gap-2">
		<UButton label="СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="!isDisabled" @click="createBillHandler()" />
		<UButton label="ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="!isDisabled" @click="createSupplyContractHandler()" />
    <UButton label="ДОГОВОР на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
      :disabled="!isDisabled" @click="createContractHandler()" />
		<UButton label="Сопроводительные документы на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			:disabled="!isDisabled" @click="inDevelopment()" />
	</div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { Editor } from '~/constants/keys';
import { useDeals } from '~/composables/useDeals';

const route = useRoute()
const router = useRouter()
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const { createBill, createContract, createSupplyContract } = useDeals()

defineProps<{
	inDevelopment: () => any
}>()

const createBillHandler = () => {
  createBill(Number(route.query.dealId))
  activeTab.value = '1'
  router.replace({...route, hash: '#bill'})
}

const createSupplyContractHandler = () => {
  createSupplyContract(Number(route.query.dealId))
  activeTab.value = '2'
  router.replace({...route, hash: '#supplyContract'})
}

const createContractHandler = () => {
  createContract(Number(route.query.dealId))
  activeTab.value = '3'
  router.replace({...route, hash: '#contract'})
}
</script>
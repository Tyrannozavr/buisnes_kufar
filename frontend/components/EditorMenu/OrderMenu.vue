<template>
	<div class="flex flex-col gap-2">
		<UButton label="СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			class="cursor-pointer"
			:disabled="isCreatingBill" :loading="isCreatingBill"
			@click="createBillHandler()" />
		<UButton label="ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			class="cursor-pointer"
			:disabled="isCreatingSupplyContract" :loading="isCreatingSupplyContract"
			@click="createSupplyContractHandler()" />
    <UButton label="ДОГОВОР на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			class="cursor-pointer"
      @click="createContractHandler()" />
		<UButton label="Сопроводительные документы на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
			class="cursor-pointer"
			@click="inDevelopment()" />
	</div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { Editor } from '~/constants/keys';
import { useDeals } from '~/composables/useDeals';

const route = useRoute()
const router = useRouter()
const toast = useToast()
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const isDisabled = useTypedState(Editor.IS_DISABLED)
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const supplyContractType = useTypedState(Editor.SUPPLY_CONTRACT_TYPE, () => ref<'supplyContract' | 'specification'>('supplyContract'))
const { createBill, createContract, createSupplyContract } = useDeals()

const isCreatingBill = ref(false)
const isCreatingSupplyContract = ref(false)

defineProps<{
	inDevelopment: () => any
}>()

const createBillHandler = async () => {
	const dealId = Number(route.query.dealId)
	if (!dealId) return

	isCreatingBill.value = true
	try {
		await createBill(dealId, { fillFromDeal: true })
		activeTab.value = '1'
		await router.replace({ ...route, hash: '#bill' })
		loadDealTrigger.value++
		isDisabled.value = false
		toast.add({
			title: 'Счёт создан',
			description: 'Данные заказа подставлены в счёт',
			color: 'success',
		})
	} catch {
		toast.add({
			title: 'Не удалось создать счёт',
			color: 'error',
		})
	} finally {
		isCreatingBill.value = false
	}
}

const createSupplyContractHandler = async () => {
	const dealId = Number(route.query.dealId)
	if (!dealId) return

	isCreatingSupplyContract.value = true
	try {
		await createSupplyContract(dealId)
		supplyContractType.value = 'supplyContract'
		activeTab.value = '2'
		await router.replace({ ...route, hash: '#supplyContract' })
		loadDealTrigger.value++
		toast.add({
			title: 'Договор поставки создан',
			description: 'Данные заказа подставлены в договор',
			color: 'success',
		})
	} catch {
		toast.add({
			title: 'Не удалось создать договор поставки',
			color: 'error',
		})
	} finally {
		isCreatingSupplyContract.value = false
	}
}

const createContractHandler = () => {
  createContract(Number(route.query.dealId))
  activeTab.value = '5'
  router.replace({...route, hash: '#contract'})
}
</script>

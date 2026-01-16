<template>
	<div>
		<UCard variant="subtle" class="top-26">

			<div class="flex flex-col justify-between gap-5">

				<div class="w-full">
					<UCollapsible>
						<UButton label="Заполнить данными" icon="i-lucide-file-input" class="w-full justify-center" />

						<template #content>
							<div class="flex-col mt-4 justify-center">
								<div class="flex gap-2">
									<div>
										<p class="w-40 text-nowrap">Последняя закупка:</p>
									</div>
									<UButton label="Товар" color="neutral" variant="subtle" class="w-full justify-center mb-2"
										@click="insertLastPurchasesGood" />
									<UButton label="Услуга" color="neutral" variant="subtle" class="w-full justify-center mb-2"
										@click="insertLastPurchasesService" />
								</div>
								<div class="flex gap-2">
									<div>
										<p class="w-40 text-nowrap">Последняя продажа:</p>
									</div>
									<UButton label="Товар" color="neutral" variant="subtle" class="w-full justify-center"
										@click="insertLastSalesGood" />
									<UButton label="Услуга" color="neutral" variant="subtle" class="w-full justify-center"
										@click="insertLastSalesService" />
								</div>
							</div>
						</template>
					</UCollapsible>
				</div>

				<div v-if="activeTab === '0'" class="flex flex-col gap-2">
					<UButton label="СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
						:disabled="activeButtons" @click="inDevelopment()" />
					<UButton label="ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
						:disabled="activeButtons" @click="inDevelopment()" />
					<UButton label="Сопроводительные документы на основании" color="neutral" variant="subtle"
						icon="i-lucide-file-plus" :disabled="activeButtons" @click="inDevelopment()" />
					<UButton label="СЧЕТ-ФАКТУРУ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
						:disabled="activeButtons" @click="inDevelopment()" />
				</div>

				<div v-if="activeTab === '1'">
					<div class="mb-2">
						<select name="documentType" class="w-full p-1.5 border rounded-lg">
							<option selected disabled>тип документа</option>
							<option>Счет на оплату</option>
							<option>Счет-договор</option>
							<option>Счет-оферта</option>
						</select>
						<input type="checkbox" name="reason" id="reason" value="off" class="mt-2 size-4">
						<label for="reason"> Основание</label>
					</div>

					<div class="mb-2">
						<select name="documentType" class="w-full p-1.5 border rounded-lg">
							<option selected disabled>Ставка НДС</option>
							<option>5</option>
							<option>7</option>
							<option>10</option>
							<option>18</option>
							<option>25</option>
						</select>
						<input type="checkbox" name="nds" id="nds" value="off" class="mt-2 size-4">
						<label for="nds"> Ставка НДС</label>
					</div>

					<div>
						<input placeholder="Срок оплаты" class="w-full p-1.5 border rounded-lg" value="">
						<br>
						<input type="checkbox" name="date" id="date" value="off" class="mt-2 size-4">
						<label for="date"> Срок оплаты</label>
					</div>
				</div>

				<div class="flex flex-row justify-between gap-1 w-full">
					<UCollapsible class="gap-3">
						<UButton @click="clearInput(), searchInCurrentDocument(activeTab, orderElement)" label="Поиск"
							icon="i-lucide-search" class="p-1 h-10 text-sm" />

						<template #content>
							<div class="mt-4 w-79 absolute">
								<input type="text" name="search" v-model="inputValue"
									@input="searchInCurrentDocument(activeTab, orderElement)"
									class=" border-emerald-500 border-2 rounded w-full leading-[1.75] px-2 text-lg " />
							</div>
							<div class="h-12"></div>
						</template>
					</UCollapsible>

					<UButton label="Печать" @click="printCurrentDocument(activeTab, orderElement)" icon="i-lucide-printer"
						class="p-1 w-[97px] h-10 text-sm" :disabled="activeButtons" />
					<UButton label="DOC" @click="downloadCurrentDocxBlob(activeTab, orderDocxBlob, billDocxBlob)"
						icon="i-lucide-dock" class="p-1 w-[81px] h-10 text-sm" :disabled="activeButtons" />
					<UButton label="PDF" @click="downloadCurrentPdf(activeTab, orderElement)" icon="i-lucide-dock"
						class="p-1 w-[77px] h-10 text-sm" :disabled="activeButtons" />
				</div>

				<div class="flex flex-col gap-2">
					<UButton @click="editButton()" label="Редактировать" icon="i-lucide-file-pen" color="neutral" variant="subtle"
						class="active:bg-green-500" />
					<div class="flex gap-2">
						<UButton label="Oчистить форму" icon="lucide:remove-formatting" color="neutral" variant="subtle"
							class="w-1/2" @click="clearCurrentForm(activeTab)" />
						<UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle"
							:disabled="!activeButtons" class="w-1/2" @click="removeCurrentDeal(activeTab)" />
					</div>
				</div>

				<div>
					<UButton label="Сохранить изменения" icon="i-lucide-save" size="xl" class="w-full justify-center"
						:disabled="activeButtons" @click="saveChanges(activeTab)" />
				</div>

				<div class="flex flex-col gap-2 text-center ">
					<p>Фото/Сканы документа</p>
					<UButton label="Выберите файл" icon="i-lucide-folder-search" color="neutral" variant="subtle" size="xl"
						class="justify-center" :disabled="activeButtons" @click="inDevelopment()" />
				</div>

				<div class="flex flex-row justify-between">
					<UButton label="Отправить контрагенту и сохранить" size="xl" class="w-full justify-center"
						:disabled="activeButtons" @click="inDevelopment()" />
					<!-- <UButton label="Сохранить"/> -->
				</div>
			</div>

		</UCard>
	</div>
</template>

<script setup lang="ts">
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import { usePdfGenerator } from '~/composables/usePdfGenerator';
import { useSearch } from '~/composables/useSearch';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import type { Insert } from '~/types/contracts';
import { Editor, TemplateElement } from '~/constants/keys';
import { useInsertState, useIsDisableState, useClearState, useSaveState, useRemoveDealState } from '~/composables/useStates';

const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const { purchases } = storeToRefs(purchasesStore)
const { sales } = storeToRefs(salesStore)
const activeTab: Ref<string> = useState(Editor.ACTIVE_TAB)
const orderElement: Ref<HTMLElement | null> = useState(TemplateElement.ORDER)

const inDevelopment = () => {
	const toast = useToast()
	toast.add({
		title: 'Кнопка находиться в разработке...',
		icon: 'i-lucide-git-compare',
	})
}

//Insert Button
const { statePurchasesGood, statePurchasesService, stateSalesGood, stateSalesService } = useInsertState()
const insertState: Ref<Insert> = useState(Editor.INSERT_STATE)

const insertLastPurchasesGood = (): void => {
	statePurchasesGood(true)
	doubleReversDisable()
}

const insertLastPurchasesService = (): void => {
	statePurchasesService(true)
	doubleReversDisable()
}

const insertLastSalesGood = (): void => {
	stateSalesGood(true)
	doubleReversDisable()
}

const insertLastSalesService = (): void => {
	stateSalesService(true)
	doubleReversDisable()
}

//DOCX
const { downloadBlob, generateDocxOrder, generateDocxBill } = useDocxGenerator()

let orderDocxBlob: Blob
let billDocxBlob: Blob

//присвоение корректного Blob в зависимости от выбранной сделки
watch(
	insertState,
	async (insert) => {
		if (purchases.value.goodsDeals && insert.purchasesStateGood) {
			const indexPurchasesGood: number = purchases.value.goodsDeals.length - 1
			if (purchases.value.goodsDeals?.[indexPurchasesGood]) {
				orderDocxBlob = await generateDocxOrder(purchases.value.goodsDeals[indexPurchasesGood])
			}

		} else if (purchases.value.servicesDeals && insert.purchasesStateService) {
			const indexPurchasesService: number = purchases.value.servicesDeals.length - 1
			if (purchases.value.servicesDeals?.[indexPurchasesService]) {
				orderDocxBlob = await generateDocxOrder(purchases.value.servicesDeals[indexPurchasesService])
			}

		} else if (sales.value.goodsDeals && insert.salesStateGood) {
			const indexSalesGood: number = sales.value.goodsDeals.length - 1
			if (sales.value.goodsDeals?.[indexSalesGood]) {
				orderDocxBlob = await generateDocxOrder(sales.value.goodsDeals[indexSalesGood])
			}

		} else if (sales.value.servicesDeals && insert.salesStateGood) {
			const indexSalesService: number = sales.value.servicesDeals.length - 1
			if (sales.value.servicesDeals?.[indexSalesService]) {
				orderDocxBlob = await generateDocxOrder(sales.value.servicesDeals[indexSalesService])
			}
		}
	},
	{ immediate: false, deep: true }
)

const downloadCurrentDocxBlob = (activeTab: string, orderDocxBlob: Blob, billDocxBlob: Blob): void => {
	if (activeTab === '0') {
		downloadBlob(orderDocxBlob, 'Order.docx')
	} else if (activeTab === '1') {
		downloadBlob(billDocxBlob, 'Bill.docx')
	}
}

//PDF
const { downloadPdf } = usePdfGenerator()

const downloadCurrentPdf = (activeTab: string, orderElement: HTMLElement | null): void => {
	if (activeTab === '0') {
		const fileName = 'Order'
		downloadPdf(orderElement, fileName)
	}
}

//Print 
const { printDocument } = usePdfGenerator()

const printCurrentDocument = (activeTab: string, orderElement: HTMLElement | null) => {
	if (activeTab === '0') {
		printDocument(orderElement)
	}
}

//Search
const { searchInDocument } = useSearch()
const inputValue: Ref<string> = ref('')

const clearInput = () => {
	inputValue.value = ''
}

const searchInCurrentDocument = (activeTab: string, orderElement: HTMLElement | null) => {
	if (activeTab === '0') {
		searchInDocument(orderElement, inputValue.value)
	}
}

//Button edit
const { reversDisable, doubleReversDisable } = useIsDisableState()
const activeButtons: Ref<boolean> = ref(false)

const editButton = () => {
	reversDisable()
	activeButtons.value = !activeButtons.value
}

//Button clearForm
const { applyClearState } = useClearState()

const clearCurrentForm = (activeTab: string) => {
	applyClearState()
}

//Button removeCurrentDeal
const { removeDeal } = useRemoveDealState()

const removeCurrentDeal = (activeTab: string) => {
	if (activeTab === '0') {
		removeDeal()
	}
}

// save button 
const { saveOrder } = useSaveState()

const saveChanges = (activeTab: string) => {
	if (activeTab === '0') {
		saveOrder()
	}
}
</script>
<template>
	<AppLayout>
		<div class="flex flex-row justify-between">

			<!-- template -->
			<div class="w-2/3 mr-5 p-3">
				<Editor @tabIndex="getTabs">
					<slot />
				</Editor>
			</div>
			<!-- editor -->
			<div class="basis-1/3">
				<UCard variant="subtle" class="  top-26">

					<div class="flex flex-col justify-between gap-5">

						<div class="w-full">
							<UCollapsible>
								<UButton label="Заполнить данными" icon="i-lucide-file-input" class="w-full justify-center" />

									<template #content >
										<div class="flex-col mt-4 justify-center">
											<div class="flex gap-2">
												<div>
													<p class="w-40 text-nowrap">Последняя закупка:</p>
												</div>
												<UButton label="Товар" color="neutral" variant="subtle" class="w-full justify-center mb-2" @click="insertLastPurchasesGood"/>
												<UButton label="Услуга" color="neutral" variant="subtle" class="w-full justify-center mb-2" @click="insertLastPurchasesService"/>
											</div>
											<div class="flex gap-2">
												<div>
													<p class="w-40 text-nowrap">Последняя продажа:</p>
												</div>
												<UButton label="Товар" color="neutral" variant="subtle" class="w-full justify-center"  @click="insertLastSalesGood"/>
												<UButton label="Услуга" color="neutral" variant="subtle" class="w-full justify-center"  @click="insertLastSalesService"/>
											</div>
										</div>
									</template>
							</UCollapsible>
						</div>

						<div class="flex flex-col gap-2">
							<UButton label="Создать СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
								:disabled="activeButtons" @click="inDevelopment()"/>
							<UButton label="Создать ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle"
								icon="i-lucide-file-plus" :disabled="activeButtons" @click="inDevelopment()"/>
							<UButton label="Создать Сопроводительные документы на основании" color="neutral" variant="subtle"
								icon="i-lucide-file-plus" :disabled="activeButtons" @click="inDevelopment()"/>
							<UButton label="Создать СЧЕТ-ФАКТУРУ на основании" color="neutral" variant="subtle"
								icon="i-lucide-file-plus" :disabled="activeButtons" @click="inDevelopment()"/>
						</div>

						<div class="flex flex-row justify-between">
							<UCollapsible class="gap-3">
								<UButton @click="clearInput(), searchInCurrentDocument(tabIndex, orderElement)" label="Поиск"
									icon="i-lucide-search" class="p-3 h-[44px]" />

								<template #content>
									<div class="mt-4 w-101 absolute">
										<input type="text" name="search" v-model="inputValue"
											@input="searchInCurrentDocument(tabIndex, orderElement)"
											class="border border-emerald-500 border-2 rounded w-full leading-[1.75] px-2 text-lg " />
									</div>
									<div class="h-12"></div>
								</template>
							</UCollapsible>

							<UButton label="Печать" @click="printCurrentDocument(tabIndex, orderElement)" icon="i-lucide-printer"
								class="p-3 w-[97px] h-[44px]" :disabled="activeButtons" />
							<UButton label="DOC" @click="downloadCurrentDocxBlob(tabIndex, orderDocxBlob, billDocxBlob)"
								icon="i-lucide-dock" class="p-3 w-[81px] h-[44px]" :disabled="activeButtons" />
							<UButton label="PDF" @click="downloadCurrentPdf(tabIndex, orderElement)" icon="i-lucide-dock"
								class="p-3 w-[77px] h-[44px]" :disabled="activeButtons" />
						</div>

						<div class="flex flex-col gap-2">
							<UButton @click="editButton()" label="Редактировать" icon="i-lucide-file-pen" color="neutral"
								variant="subtle" class="active:bg-green-500" />
								<div class="flex gap-2">
									<UButton label="Oчистить форму" icon="lucide:remove-formatting" color="neutral" variant="subtle"
										 class="w-1/2" @click="clearCurrentForm(tabIndex)"/>
									<UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle"
										:disabled="!activeButtons" class="w-1/2" @click="removeCurrentDeal(tabIndex)"/>
								</div>
						</div>

						<div>
							<UButton label="Сохранить документ" icon="i-lucide-save" size="xl" class="w-full justify-center"
								:disabled="activeButtons" @click="inDevelopment()"/>
						</div>

						<div class="flex flex-col gap-2 text-center ">
							<p>Фото/Сканы документа</p>
							<UButton label="Выберите файл" icon="i-lucide-folder-search" color="neutral" variant="subtle" size="xl"
								class="justify-center" :disabled="activeButtons" @click="inDevelopment()"/>
						</div>

						<div class="flex flex-row justify-between">
							<UButton label="Отправить контрагенту и сохранить" size="xl" class="w-full justify-center"
								:disabled="activeButtons" @click="inDevelopment()"/>
							<!-- <UButton label="Сохранить"/> -->
						</div>
					</div>

				</UCard>
			</div>

		</div>
	</AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '~/components/layout/AppLayout.vue';
import Editor from '~/pages/profile/contracts/editor.vue';
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import { usePdfGenerator } from '~/composables/usePdfGenerator';
import { useSearch } from '~/composables/useSearch';
import { usePurchasesStore } from '~/stores/purchases';
import type { Insert } from '~/types/contracts';

const purchasesStore = usePurchasesStore()
const { purchases } = storeToRefs(purchasesStore)

let tabIndex: string
function getTabs(activeTab: string): void {
	tabIndex = activeTab
}

const inDevelopment = () => {
	const toast = useToast()
	toast.add({
		title: 'Кнопка находиться в разработке...',
		icon: 'i-lucide-git-compare',
	})
}

//Insert Button
const insertState: Ref<Insert> = ref({
	purchasesStateGood: false,
	purchasesStateService: false,
	salesStateGood: false,
	salesStateService: false,
})

provide('insertState', insertState)

const insertLastPurchasesGood = (): void => {
	insertState.value.purchasesStateGood = !insertState.value.purchasesStateGood
	disabledInput.value = !disabledInput.value
	disabledInput.value = !disabledInput.value
}

const insertLastPurchasesService = (): void => {
	insertState.value.purchasesStateService = !insertState.value.purchasesStateService
	disabledInput.value = !disabledInput.value
	disabledInput.value = !disabledInput.value
}
const insertLastSalesGood = (): void => {
	insertState.value.salesStateGood = !insertState.value.salesStateGood
	disabledInput.value = !disabledInput.value
	disabledInput.value = !disabledInput.value
}

const insertLastSalesService = (): void => {
	insertState.value.salesStateService = !insertState.value.salesStateService
	disabledInput.value = !disabledInput.value
	disabledInput.value = !disabledInput.value
}

//DOCX
const { downloadBlob, generateDocxOrder, generateDocxBill } = useDocxGenerator()

let orderDocxBlob: Blob
let billDocxBlob: Blob

watch(
	() => purchases.value,
	async () => {
		if (purchases.value.goodsDeals?.[0]) {
			orderDocxBlob = await generateDocxOrder(purchases.value.goodsDeals[0])
			billDocxBlob = await generateDocxBill(purchases.value.goodsDeals[0])
		}
	},
	{ immediate: true, deep: true }
)

const downloadCurrentDocxBlob = (tabIndex: string, orderDocxBlob: Blob, billDocxBlob: Blob): void => {
	if (tabIndex === '0') {
		downloadBlob(orderDocxBlob, 'Order.docx')
	} else if (tabIndex === '1') {
		downloadBlob(billDocxBlob, 'Bill.docx')
	}
}

//PDF
const { downloadPdf } = usePdfGenerator()
const orderElement: Ref<HTMLElement | null> = useState('htmlOrder')

const downloadCurrentPdf = (tabIndex: string, orderElement: HTMLElement | null): void => {
	if (tabIndex === '0') {
		const fileName = 'Order'
		downloadPdf(orderElement, fileName)
	}
}

//Print 
const { printDocument } = usePdfGenerator()

const printCurrentDocument = (tabIndex: string, orderElement: HTMLElement | null) => {
	if (tabIndex === '0') {
		printDocument(orderElement)
	}
}

//Search
const { searchInDocument } = useSearch()
const inputValue: Ref<string> = ref('')

const clearInput = () => {
	inputValue.value = ''
}

const searchInCurrentDocument = (tabIndex: string, orderElement: HTMLElement | null) => {
	if (tabIndex === '0') {
		searchInDocument(orderElement, inputValue.value)
	}
}

//Button edit
let disabledInput: Ref<boolean> = ref(true)
let activeButtons: Ref<boolean> = ref(false)

provide('disabledInput', disabledInput)

const editButton = () => {
	disabledInput.value = !disabledInput.value
	activeButtons.value = !activeButtons.value
}

//Button clearForm
let clearState: Ref<boolean> = ref(false)

provide('clearState', clearState)

const clearCurrentForm = (tabIndex: string) => {
	if (tabIndex === '0') {
		clearState.value = !clearState.value
		setTimeout(
			() => {
				clearState.value = !clearState.value
			}, 0
		)
	}
}

//Button removeCurrentDeal
let removeDealState: Ref<Boolean> = ref(false)

provide('removeDealState', removeDealState)

const removeCurrentDeal = (tabIndex: string) => {
	if (tabIndex === '0') {
		removeDealState.value = !removeDealState.value
		removeDealState.value = !removeDealState.value
	}
}


</script>

<style scoped>
/* div UButton {
	margin: 3px;
}
div {
	margin: 5px;
} */
</style>
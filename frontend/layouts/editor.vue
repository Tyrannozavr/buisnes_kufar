<template>
	<AppLayout>
		<div class="flex flex-row justify-between">

			<!-- template -->
			<div class="w-[70%] mr-3 h-[100%] overflow-y-hidden">
				<slot />
			</div>
			<!-- editor -->
			<div class="w-[30%]">
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
							<UButton label="СЧЕТ на основании" color="neutral" variant="subtle" icon="i-lucide-file-plus"
								:disabled="isEditing" @click="inDevelopment()"/>
							<UButton label="ДОГОВОР ПОСТАВКИ на основании" color="neutral" variant="subtle"
								icon="i-lucide-file-plus" :disabled="isEditing" @click="inDevelopment()"/>
							<UButton label="Сопроводительные документы на основании" color="neutral" variant="subtle"
								icon="i-lucide-file-plus" :disabled="isEditing" @click="inDevelopment()"/>
							<UButton label="СЧЕТ-ФАКТУРУ на основании" color="neutral" variant="subtle"
								icon="i-lucide-file-plus" :disabled="isEditing" @click="inDevelopment()"/>
						</div>

						<div class="flex flex-row justify-between gap-1 w-full">
							<UCollapsible class="gap-3">
								<UButton @click="clearInput(), searchInCurrentDocument()" label="Поиск"
									icon="i-lucide-search" class="p-1 h-10 text-sm" />

								<template #content>
									<div class="mt-4 w-79 absolute">
										<input type="text" name="search" v-model="inputValue"
											@input="searchInCurrentDocument()"
											class=" border-emerald-500 border-2 rounded w-full leading-[1.75] px-2 text-lg " />
									</div>
									<div class="h-12"></div>
								</template>
							</UCollapsible>

							<UButton label="Печать" @click="printCurrentDocument()" icon="i-lucide-printer"
								class="p-1 w-[97px] h-10 text-sm" :disabled="isEditing" />
							<UButton label="DOC" @click="downloadCurrentDocxBlob()"
								icon="i-lucide-dock" class="p-1 w-[81px] h-10 text-sm" :disabled="isEditing" />
							<UButton label="PDF" @click="downloadCurrentPdf()" icon="i-lucide-dock"
								class="p-1 w-[77px] h-10 text-sm" :disabled="isEditing" />
						</div>

						<div class="flex flex-col gap-2">
							<UButton @click="editButton()" label="Редактировать" icon="i-lucide-file-pen" color="neutral"
								variant="subtle" class="active:bg-green-500" />
								<div class="flex gap-2">
									<UButton label="Oчистить форму" icon="lucide:remove-formatting" color="neutral" variant="subtle"
										 class="w-1/2" @click="clearCurrentForm(tabIndex)"/>
									<UButton label="Удалить сделку" icon="i-lucide-file-x" color="neutral" variant="subtle"
										:disabled="!isEditing" class="w-1/2" @click="removeCurrentDeal(tabIndex)"/>
								</div>
						</div>

						<div>
							<UButton label="Сохранить изменения" icon="i-lucide-save" size="xl" class="w-full justify-center"
								:disabled="!isEditing" @click="saveChanges(tabIndex)"/>
						</div>

						<div class="flex flex-col gap-2 text-center ">
							<p>Фото/Сканы документа</p>
							<UButton label="Выберите файл" icon="i-lucide-folder-search" color="neutral" variant="subtle" size="xl"
								class="justify-center" :disabled="isEditing" @click="inDevelopment()"/>
						</div>

						<div class="flex flex-row justify-between">
							<UButton label="Отправить контрагенту и сохранить" size="xl" class="w-full justify-center"
								:disabled="isEditing" @click="inDevelopment()"/>
							<!-- <UButton label="Сохранить"/> -->
						</div>
					</div>

				</UCard>
			</div>

		</div>
	</AppLayout>
</template>

<script setup lang="ts">
// Формы документов по сделке: загрузка/сохранение — GET/PUT /api/v1/purchases/{deal_id}/documents/{document_type}.
// Подробно: docs/DOCUMENTS_API_FRONTEND.md (при открытии вкладки — GET, кнопка «Сохранить» — PUT с payload).
import AppLayout from '~/components/layout/AppLayout.vue';
import { useDocxGenerator } from '~/composables/useDocxGenerator';
import { usePdfGenerator } from '~/composables/usePdfGenerator';
import { useSearch } from '~/composables/useSearch';
import { usePurchasesStore } from '~/stores/purchases';
import { useSalesStore } from '~/stores/sales';
import type { Insert } from '~/types/contracts';
import { injectionKeys } from '~/constants/keys';

const purchasesStore = usePurchasesStore()
const salesStore = useSalesStore()
const { purchases } = storeToRefs(purchasesStore)
const { sales } = storeToRefs(salesStore)

// Активная вкладка редактора документа (индекс number — синхронно с UTabs на странице editor)
const tabIndex = useState<number>('editorTabIndex', () => 0)

const inDevelopment = () => {
	const toast = useToast()
	toast.add({
		title: 'Кнопка находиться в разработке...',
		icon: 'i-lucide-git-compare',
	})
}

// Insert: общий стейт через useState, чтобы и layout (кнопки), и Order (watch) видели одни данные
const insertState = useState<Insert>('editorInsertState', () => ({
	purchasesStateGood: false,
	purchasesStateService: false,
	salesStateGood: false,
	salesStateService: false,
}))
provide(injectionKeys.insertStateKey, insertState)

const insertLastPurchasesGood = (): void => {
	insertState.value.purchasesStateGood = !insertState.value.purchasesStateGood
}

const insertLastPurchasesService = (): void => {
	insertState.value.purchasesStateService = !insertState.value.purchasesStateService
}

const insertLastSalesGood = (): void => {
	insertState.value.salesStateGood = !insertState.value.salesStateGood
}

const insertLastSalesService = (): void => {
	insertState.value.salesStateService = !insertState.value.salesStateService
}

//DOCX
const { downloadBlob, generateDocxOrder, generateDocxBill } = useDocxGenerator()

let orderDocxBlob: Blob
let billDocxBlob: Blob

//присвоение корректного Blob в зависимости от выбранной сделки
watch(
	() => insertState.value,
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

		} else if (sales.value.servicesDeals && insert.salesStateService) {
			const indexSalesService: number = sales.value.servicesDeals.length - 1 
			if (sales.value.servicesDeals?.[indexSalesService]) {
				orderDocxBlob = await generateDocxOrder(sales.value.servicesDeals[indexSalesService])
			}
		}
	},
	{ immediate: false, deep: true }
)

const downloadCurrentDocxBlob = (): void => {
	if (tabIndex.value === 0) {
		downloadBlob(orderDocxBlob, 'Order.docx')
	} else if (tabIndex.value === 1) {
		downloadBlob(billDocxBlob, 'Bill.docx')
	}
}

//PDF
const { downloadPdf } = usePdfGenerator()
const orderElement: Ref<HTMLElement | null> = useState('htmlOrder')

const downloadCurrentPdf = (): void => {
	if (tabIndex.value === 0) {
		const fileName = 'Order'
		downloadPdf(orderElement.value, fileName)
	}
}

//Print 
const { printDocument } = usePdfGenerator()

const printCurrentDocument = () => {
	if (tabIndex.value === 0) {
		printDocument(orderElement.value)
	}
}

//Search
const { searchInDocument } = useSearch()
const inputValue: Ref<string> = ref('')

const clearInput = () => {
	inputValue.value = ''
}

const searchInCurrentDocument = () => {
	if (tabIndex.value === 0) {
		searchInDocument(orderElement.value, inputValue.value)
	}
}

//Button edit
const isDisabled: Ref<boolean> = ref(true)
const isEditing = computed(() => !isDisabled.value)

provide(injectionKeys.isDisabledKey, isDisabled)

const editButton = () => {
	isDisabled.value = !isDisabled.value
}

//Button clearForm
const clearState: Ref<boolean> = ref(false)

provide(injectionKeys.clearStateKey, clearState)

const clearCurrentForm = (tabRef: Ref<number>) => {
	if (tabRef.value === 0) {
		clearState.value = !clearState.value
		setTimeout(
			() => {
				clearState.value = !clearState.value
			}, 0
		)
	}
}

//Button removeCurrentDeal
const removeDealState: Ref<Boolean> = ref(false)

provide(injectionKeys.removeDealStateKey, removeDealState)

const removeCurrentDeal = (tabRef: Ref<number>) => {
	if (tabRef.value === 0) {
		// ВАЖНО: не переключаем дважды подряд — иначе значение не меняется
		// и watcher в шаблоне не срабатывает.
		removeDealState.value = !removeDealState.value
	}
}

// save button 
const changeState: Ref<Boolean> = ref(false)

provide(injectionKeys.changeStateOrderKey, changeState)

const saveChanges = (tabRef: Ref<number>) => {
	if (tabRef.value === 0) {
		// ВАЖНО: не переключаем дважды подряд — иначе watcher не срабатывает.
		changeState.value = !changeState.value
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
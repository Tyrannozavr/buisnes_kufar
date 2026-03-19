<template>
	<div>
		<UCard variant="subtle" class="top-26">
			<div v-if="confirmation" class="flex flex-col justify-between gap-5">
				<UButton
					label="Принять изменения"
					icon="i-lucide-check"
					color="success"
					variant="solid"
					class="w-full justify-center"
					@click="confirm()"
				/>
				<UButton
					label="Отклонить изменения"
					icon="i-lucide-x"
					color="error"
					variant="soft"
					class="w-full justify-center"
					@click="(reject(), clearCurrentForm(activeTab))"
				/>
			</div>

			<div v-else class="flex flex-col justify-between gap-5">
				<InsertButtons :isCancelChanges="isCancelChanges" />

				<div :hidden="isHiddenForBuyer" v-if="activeTab === '0'">
					<OrderMenu :inDevelopment />
				</div>

				<div :hidden="isHiddenForBuyer" v-if="activeTab === '1'">
					<BillMenu  />
				</div>

				<div class="flex flex-row justify-between gap-1 w-full">
					<UCollapsible class="gap-3">
						<UButton
							@click="(clearInput(), searchInCurrentDocument(activeTab, orderElement))"
							label="Поиск"
							icon="i-lucide-search"
							class="p-1 h-10 text-sm"
						/>

						<template #content>
							<div class="mt-4 w-79 absolute">
								<input
									type="text"
									name="search"
									v-model="inputValue"
									@input="searchInCurrentDocument(activeTab, orderElement)"
									class="border-emerald-500 border-2 rounded w-full leading-[1.75] px-2 text-lg"
								/>
							</div>
							<div class="h-12"></div>
						</template>
					</UCollapsible>

					<UButton
						label="Печать"
						@click="printCurrentDocument(activeTab, orderElement)"
						icon="i-lucide-printer"
						class="p-1 w-[97px] h-10 text-sm"
						:disabled="!isDisabled"
					/>
					<UButton
						label="DOC"
						@click="downloadCurrentDocxBlob(activeTab)"
						icon="i-lucide-dock"
						class="p-1 w-[81px] h-10 text-sm"
						:disabled="!isDisabled"
					/>
					<UButton
						label="PDF"
						@click="downloadCurrentPdf(activeTab, orderElement)"
						icon="i-lucide-dock"
						class="p-1 w-[77px] h-10 text-sm"
						:disabled="!isDisabled"
					/>
				</div>

				<div class="flex flex-col gap-2">
					<UButton
						:disabled="!isDisabled"
						@click="editButton()"
						label="Редактировать"
						icon="i-lucide-file-pen"
						color="neutral"
						variant="subtle"
						class="active:bg-green-500"
					/>

					<div class="flex gap-2">
						<UButton
							label="Oчистить форму"
							icon="lucide:remove-formatting"
							color="neutral"
							variant="subtle"
							class="w-1/2"
							@click="clearCurrentForm(activeTab)"
						/>

						<UModal
							v-model:open="modalIsOpen"
							title="Вы уверены, что хотите удалить сделку?"
							description="Удаление сделки приведет к удалению всех данных у вас и у контрагента"
						>
							<UButton
								label="Удалить сделку"
								icon="i-lucide-file-x"
								color="neutral"
								variant="subtle"
								class="w-1/2"
							/>

							<template #footer>
								<UButton
									label="Удалить сделку"
									icon="i-lucide-file-x"
									color="neutral"
									variant="subtle"
									class="w-1/2"
									@click="(removeCurrentDeal(), (modalIsOpen = false))"
								/>
								<UButton
									label="Отмена"
									icon="i-lucide-x"
									color="neutral"
									variant="subtle"
									class="w-1/2"
									@click="modalIsOpen = false"
								/>
							</template>
						</UModal>
					</div>
				</div>

				<div class="flex flex-col gap-2 text-center">
					<p>Фото/Сканы документа</p>
					<UButton
						label="Выберите файл"
						icon="i-lucide-folder-search"
						color="neutral"
						variant="subtle"
						size="xl"
						class="justify-center"
						:disabled="!isDisabled"
						@click="inDevelopment()"
					/>
				</div>

				<div v-if="!isDisabled" class="">
					<UButton
						label="Отменить изменения"
						size="lg"
						class="w-full justify-center"
						color="neutral"
						variant="subtle"
						:disabled="isDisabled"
						@click="(cancelChanges(activeTab), editButton())"
					/>
				</div>

				<div class="flex flex-row justify-between">
					<UButton
						label="Отправить контрагенту и сохранить"
						size="xl"
						class="w-full justify-center"
						:disabled="isDisabled"
						@click="modalIsOpenSaveChanges = true"
					/>
				</div>
			</div>
		</UCard>
	</div>
	<UModal v-model:open="modalIsOpenSaveChanges" title="Данные будут изменены. Продолжить?">
		<template #body class="flex flex-row justify-between gap-2">
			<div class="flex flex-row justify-between gap-2">
			<UButton label="Отмена" icon="i-lucide-x" color="neutral" variant="subtle" class="w-1/2" @click="modalIsOpenSaveChanges = false" />
			<UButton
				label="Продолжить"
				icon="i-lucide-check"
				color="success"
				variant="subtle"
				class="w-1/2"
				@click="
					saveChanges(),
					sendMessageToCounterpart(
						Number(route.query.dealId),
						route.query.role as 'buyer' | 'seller',
						counterpartData as CounterpartData
					),
					modalIsOpenSaveChanges = false
				"
			/>
			</div>
		</template>
	</UModal>
</template>

<script setup lang="ts">
import InsertButtons from "./InsertButtons.vue"
import OrderMenu from "./OrderMenu.vue"
import BillMenu from "./BillMenu.vue"
import { useDocxGenerator } from "~/composables/useDocxGenerator"
import { usePdfGenerator } from "~/composables/usePdfGenerator"
import { useSearch } from "~/composables/useSearch"
import { Editor, TemplateElement } from "~/constants/keys"
import {
	useClearState,
	useRemoveDealState
} from "~/composables/useStates"
import { useSaveDeals } from "~/composables/useSaveDeals"
import { useRoute } from "vue-router"
import {
	getCounterpartData,
	sendMessageToCounterpart
} from "~/utils/counterpart"
import type { CounterpartData } from "~/utils/counterpart"
import { useDeals } from "~/composables/useDeals"

const modalIsOpen = ref(false)
const route = useRoute()
const router = useRouter()
const { deals, lastDeal } = useDeals()
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const orderElement = useTypedState(TemplateElement.ORDER)
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const { createNewDealVersion, deleteLastDealVersion } = useDeals()

const inDevelopment = () => {
	const toast = useToast()
	toast.add({
		title: "Кнопка находиться в разработке...",
		icon: "i-lucide-git-compare"
	})
}

//Hidden buttons for buyer
const isHiddenForBuyer = computed(() => {
	return route.query.role === "buyer"
})

//DOCX
const { downloadBlob, generateDocxOrder, generateDocxBill } = useDocxGenerator()

let orderDocxBlob: Blob | null = null
let billDocxBlob: Blob | null = null

//присвоение корректного Blob в зависимости от выбранной сделки
watch(
	route.query,
	async () => {
		if (deals && route.query.dealType === "purchases") {
			if (lastDeal?.value?.purchases) {
				orderDocxBlob = await generateDocxOrder(lastDeal?.value?.purchases)
			}
		} else if (deals && route.query.dealType === "sales") {
			if (lastDeal?.value?.sales) {
				orderDocxBlob = await generateDocxOrder(lastDeal?.value?.sales)
			}
		}
	},
	{ immediate: false, deep: true }
)

const downloadCurrentDocxBlob = async (activeTab: string): Promise<void> => {
	if (activeTab === "0" && orderDocxBlob) {
		downloadBlob(orderDocxBlob, "Order.docx")
	} else if (activeTab === "1") {
		if (!billDocxBlob) {
			// Генерируем billDocxBlob динамически при необходимости
			// TODO: передать нужные данные для генерации Bill
			return
		}
		downloadBlob(billDocxBlob, "Bill.docx")
	}
}

//PDF
const { downloadPdf } = usePdfGenerator()

const downloadCurrentPdf = (
	activeTab: string,
	orderElement: HTMLElement | null
): void => {
	if (activeTab === "0") {
		const fileName = "Order"
		downloadPdf(orderElement, fileName)
	}
}

//Print
const { printDocument } = usePdfGenerator()

const printCurrentDocument = (
	activeTab: string,
	orderElement: HTMLElement | null
) => {
	if (activeTab === "0") {
		printDocument(orderElement)
	}
}

//Search
const { searchInDocument } = useSearch()
const inputValue: Ref<string> = ref("")

const clearInput = () => {
	inputValue.value = ""
}

const searchInCurrentDocument = (
	activeTab: string,
	orderElement: HTMLElement | null
) => {
	if (activeTab === "0") {
		searchInDocument(orderElement, inputValue.value)
	}
}

//Button edit
const editButton = () => {
	isDisabled.value = !isDisabled.value
}

//Button clearForm
const { applyClearState } = useClearState()

const clearCurrentForm = (activeTab: string) => {
	applyClearState()
}

//Button removeCurrentDeal
const { removeDeal } = useRemoveDealState()

const removeCurrentDeal = () => {
		removeDeal()
}

// save button
const { startSave } = useSaveDeals()
const modalIsOpenSaveChanges = ref(false)


const counterpartData: CounterpartData | null = getCounterpartData(
	Number(route.query.dealId),
	route.query.role as "buyer" | "seller"
)

const saveChanges = async (): Promise<void> => {
	try {
		// Сначала сохраняем форму в store (officials, products и т.д.), затем создаём новую версию.
		await startSave()
		await createNewDealVersion(Number(route.query.dealId))
		editButton()

		useToast().add({
			title: "Изменения сохранены и отправлены контрагенту",
			color: "success"
		})
	} catch (err) {
		console.error("Ошибка при отправке контрагенту:", err)
		useToast().add({
			title: "Ошибка при отправке сообщения контрагенту",
			color: "error"
		})
	}
}

// cancel button
const isCancelChanges: Ref<{
	sales: boolean
	purchases: boolean
}> = ref({
	sales: false,
	purchases: false
})

const cancelChanges = (activeTab: string) => {
	const role = route.query.role

	if (role === "seller") {
		isCancelChanges.value.sales = !isCancelChanges.value.sales
	} else if (role === "buyer") {
		isCancelChanges.value.purchases = !isCancelChanges.value.purchases
	}
}

//подтверждение изменений при изменении заказа одной из сторон
const confirmation = ref(false)

watch(
	() => route.fullPath,
	() => {
		confirmation.value = route.query.confirmation === "true" ? true : false
	},
	{ immediate: true, deep: true }
)

const confirm = () => {
	router.replace({ query: { ...route.query, confirmation: "false" } })
	sendMessageToCounterpart(
		Number(route.query.dealId),
		route.query.role as "buyer" | "seller",
		counterpartData as CounterpartData,
		true
	) //true если изменения приняты

	useToast().add({
		title: "Изменения приняты",
		color: "success"
	})
}

const reject = async () => {
	router.replace({ query: { ...route.query, confirmation: "false" } })
	sendMessageToCounterpart(
		Number(route.query.dealId),
		route.query.role as "buyer" | "seller",
		counterpartData as CounterpartData,
		false
	) //false если изменения отклонены
	const dealId = Number(route.query.dealId)

	if (dealId) {
		await deleteLastDealVersion(dealId)
	}

	useToast().add({
		title: "Изменения отклонены",
		color: "warning"
	})
}
</script>

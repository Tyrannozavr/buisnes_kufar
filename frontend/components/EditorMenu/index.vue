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

				<div v-if="activeTab === '1'">
					<BillMenu :hiddenForBuyer="isHiddenForBuyer" />
				</div>

				<div class="flex flex-row justify-between gap-1 w-full">
					<UCollapsible class="gap-3">
						<UButton
							@click="(clearInput(), searchInCurrentDocument(activeTab))"
							label="Поиск"
							icon="i-lucide-search"
							class="p-1 h-10 text-sm"
						/>

						<template #content>
							<div class="mt-4 w-79 absolute flex flex-col gap-2">
								<input
									type="text"
									name="search"
									v-model="inputValue"
									@input="searchInCurrentDocument(activeTab)"
									@keydown="handleSearchKeydown"
									placeholder="Поиск по документу…"
									class="border-emerald-500 border-2 rounded w-full leading-[1.75] px-2 text-lg"
									autocomplete="off"
									aria-label="Поиск по документу"
								/>
								<div
									v-if="matchTotal > 0"
									class="flex items-center justify-between gap-2 text-sm text-neutral-600 dark:text-neutral-400"
								>
									<div class="flex items-center gap-1">
										<UButton
											type="button"
											icon="i-lucide-chevron-up"
											size="xs"
											variant="soft"
											color="neutral"
											class="p-1 min-w-8"
											aria-label="Предыдущее вхождение"
											@click="goToPreviousMatch"
										/>
										<UButton
											type="button"
											icon="i-lucide-chevron-down"
											size="xs"
											variant="soft"
											color="neutral"
											class="p-1 min-w-8"
											aria-label="Следующее вхождение"
											@click="goToNextMatch"
										/>
									</div>
									<span class="tabular-nums font-medium" aria-live="polite">
										{{ matchCurrent }} / {{ matchTotal }}
									</span>
								</div>
								<p class="text-xs text-neutral-500 dark:text-neutral-500">
									Enter — далее, Shift+Enter — назад
								</p>
							</div>
							<div class="h-24"></div>
						</template>
					</UCollapsible>

					<UButton
						label="Печать"
						@click="printCurrentDocument(activeTab)"
						icon="i-lucide-printer"
						class="p-1 w-[97px] h-10 text-sm"
						:disabled="!isDisabled"
					/>
					<UButton
						label="DOC"
						@click="handleDownloadCurrentDocx(activeTab)"
						icon="i-lucide-dock"
						class="p-1 w-[81px] h-10 text-sm"
						:disabled="!isDisabled"
					/>
					<UButton
						label="PDF"
						@click="handleDownloadCurrentPdf(activeTab)"
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
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const orderElement = useTypedState(TemplateElement.ORDER)
const billElement = useTypedState(TemplateElement.BILL)
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const billType = useTypedState(Editor.BILL_TYPE)
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

//DOCX / PDF — с бэкенда (docxtpl + Gotenberg), см. docs/DOCX_TEMPLATES_BACKEND.md
const { downloadDealGeneratedDocx, downloadDealGeneratedPdf } = useDocxGenerator()

const handleDownloadCurrentDocx = async (tab: string): Promise<void> => {
	const dealId = Number(route.query.dealId)
	if (!dealId || Number.isNaN(dealId)) {
		useToast().add({ title: "Не выбрана сделка", color: "error" })
		return
	}
	try {
		if (tab === "0") {
			await downloadDealGeneratedDocx(dealId, "order")
			return
		}
		if (tab === "1") {
			const selected = billType.value as { value?: string } | null | undefined
			const sub = selected?.value ?? "bill"
			const variant =
				sub === "bill-contract"
					? "bill-contract"
					: sub === "bill-offer"
						? "bill-offer"
						: "bill"
			await downloadDealGeneratedDocx(dealId, variant)
		}
	} catch (e) {
		console.error(e)
		useToast().add({
			title: "Не удалось скачать документ",
			color: "error",
		})
	}
}

const handleDownloadCurrentPdf = async (tab: string): Promise<void> => {
	const dealId = Number(route.query.dealId)
	if (!dealId || Number.isNaN(dealId)) {
		useToast().add({ title: "Не выбрана сделка", color: "error" })
		return
	}
	try {
		if (tab === "0") {
			await downloadDealGeneratedPdf(dealId, "order")
			return
		}
		if (tab === "1") {
			const selected = billType.value as { value?: string } | null | undefined
			const sub = selected?.value ?? "bill"
			const variant =
				sub === "bill-contract"
					? "bill-contract"
					: sub === "bill-offer"
						? "bill-offer"
						: "bill"
			await downloadDealGeneratedPdf(dealId, variant)
		}
	} catch (e) {
		console.error(e)
		useToast().add({
			title: "Не удалось скачать PDF (нужен Gotenberg и GOTENBERG_URL на бэкенде)",
			color: "error",
		})
	}
}

// Print: innerHTML не содержит .value у input/textarea — без replaceTextareasAndInputs в печати пустые поля и placeholder
const { printDocument, replaceTextareasAndInputs } = usePdfGenerator()

const printCurrentDocument = (activeTab: string) => {
	const root =
		activeTab === "0"
			? orderElement.value
			: activeTab === "1"
				? billElement.value
				: null
	if (!root) {
		return
	}
	const cloneWithText = replaceTextareasAndInputs(root)
	printDocument(cloneWithText)
}

//Search (как Ctrl+F: вхождения, счётчик, вперёд/назад, Enter / Shift+Enter)
const {
	searchInDocument,
	goToNextMatch,
	goToPreviousMatch,
	handleSearchKeydown,
	matchTotal,
	matchCurrent,
} = useSearch()
const inputValue: Ref<string> = ref("")

const clearInput = () => {
	inputValue.value = ""
}

const searchInCurrentDocument = (activeTab: string) => {
	const root =
		activeTab === "0"
			? orderElement.value
			: activeTab === "1"
				? billElement.value
				: null
	if (!root) {
		return
	}
	searchInDocument(root, inputValue.value)
}

watch(
	() => activeTab.value,
	() => {
		if (inputValue.value.trim()) {
			searchInCurrentDocument(String(activeTab.value ?? "0"))
		}
	}
)

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

<template>
	<div>
		<UCard variant="subtle" class="top-26">
			<div class="flex flex-col gap-5">
			<div v-if="canRespondToChanges" class="flex flex-col justify-between gap-5">
				<p class="text-sm text-neutral-500 text-center px-1">
					Слева — предложенная версия. Изменения в <strong>заказе</strong> (позиции, сумма, комментарий)
					выделяются цветом на бланке «Заказ».
				</p>
				<p
					v-if="billTypeChangeSummary || billDateChangeSummary"
					class="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded-md px-3 py-2 text-center"
				>
					<span v-if="billTypeChangeSummary">{{ billTypeChangeSummary }}</span>
					<span v-if="billDateChangeSummary">
						<br v-if="billTypeChangeSummary" />
						{{ billDateChangeSummary }}
					</span>
					<br />
					<span class="text-xs text-amber-700">Смотрите также вкладку «Счет» — изменения выделены жёлтым.</span>
				</p>
				<p
					v-else-if="!hasOrderVisualDiff"
					class="text-sm text-neutral-600 bg-neutral-100 rounded-md px-3 py-2 text-center"
				>
					В позициях заказа отличий нет. Контрагент сохранил новую версию сделки
					(часто — правки счёта или других полей). Примите или отклоните версию.
				</p>
				<p v-if="changeReview?.diff?.items?.length" class="text-xs text-neutral-400 text-center px-1">
					<span class="inline-block w-3 h-3 bg-amber-200 border border-amber-300 align-middle mr-1" />
					изменено
					<span class="inline-block w-3 h-3 bg-green-100 border border-green-300 align-middle mx-1" />
					добавлено
					<span class="inline-block w-3 h-3 bg-red-100 border border-red-300 align-middle mx-1" />
					удалено
				</p>
				<p class="text-xs text-neutral-500 text-center px-1">
					Сканы документа (фото/PDF) — в блоке «Фото/Сканы» ниже, отдельно от согласования заказа.
				</p>
				<UButton
					label="Принять изменения"
					icon="i-lucide-check"
					color="success"
					variant="solid"
					class="w-full justify-center"
					:loading="changeReviewActionLoading"
					@click="confirm()"
				/>
				<UButton
					label="Отклонить изменения"
					icon="i-lucide-x"
					color="error"
					variant="soft"
					class="w-full justify-center"
					:loading="changeReviewActionLoading"
					@click="reject()"
				/>
			</div>

			<div v-else class="flex flex-col justify-between gap-5">
				<p
					v-if="pendingReviewHint"
					class="text-sm text-neutral-500 text-center px-1"
				>
					Изменения отправлены контрагенту. Ожидайте ответа.
				</p>
				<InsertButtons v-if="!isHiddenForBuyer" />

				<div v-if="activeTab === '0' && !isBuyerRole">
					<OrderMenu :inDevelopment />
				</div>

				<div v-if="activeTab === '1'">
					<BillMenu :hiddenForBuyer="isHiddenForBuyer" />
				</div>

				<div v-if="activeTab === '2' && !isHiddenForBuyer">
					<SupplyContractMenu />
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

					<UTooltip :text="tooltipPreviewExport" :disabled="!tooltipPreviewExport">
						<span class="inline-block" :class="{ 'cursor-not-allowed': tooltipPreviewExport }">
							<UButton
								label="Печать"
								@click="printCurrentDocument(activeTab)"
								icon="i-lucide-printer"
								class="p-1 w-[97px] h-10 text-sm"
								:disabled="!isDisabled"
							/>
						</span>
					</UTooltip>
					<UTooltip :text="tooltipPreviewExport" :disabled="!tooltipPreviewExport">
						<span class="inline-block" :class="{ 'cursor-not-allowed': tooltipPreviewExport }">
							<UButton
								label="DOC"
								@click="handleDownloadCurrentDocx(activeTab)"
								icon="i-lucide-dock"
								class="p-1 w-[81px] h-10 text-sm"
								:loading="isDocxDownloading"
								:disabled="!isDisabled || isDocxDownloading"
							/>
						</span>
					</UTooltip>
					<UTooltip :text="tooltipPreviewExport" :disabled="!tooltipPreviewExport">
						<span class="inline-block" :class="{ 'cursor-not-allowed': tooltipPreviewExport }">
							<UButton
								label="PDF"
								@click="handleDownloadCurrentPdf(activeTab)"
								icon="i-lucide-dock"
								class="p-1 w-[77px] h-10 text-sm"
								:loading="isPdfDownloading"
								:disabled="!isDisabled || isPdfDownloading"
							/>
						</span>
					</UTooltip>
				</div>

				<p
					v-if="!isHiddenForBuyer && isDisabled"
					class="text-xs text-neutral-500 dark:text-neutral-400 text-center -mt-1"
				>
					Режим просмотра. Нажмите «Редактировать» для правок.
				</p>

				<div v-if="!isHiddenForBuyer" class="flex flex-col gap-2">
					<UTooltip :text="tooltipEdit" :disabled="!tooltipEdit">
						<span class="block w-full" :class="{ 'cursor-not-allowed': tooltipEdit }">
							<UButton
								:disabled="!isDisabled"
								@click="editButton()"
								label="Редактировать"
								icon="i-lucide-file-pen"
								color="neutral"
								variant="subtle"
								class="active:bg-green-500 w-full justify-center"
							/>
						</span>
					</UTooltip>

					<div class="flex gap-2">
						<UButton
							label="Удалить данные"
							icon="lucide:remove-formatting"
							color="neutral"
							variant="subtle"
							class="w-1/2"
							@click="clearCurrentForm(activeTab)"
						/>

						<UModal
							v-if="!isBuyerRole"
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

				<div v-if="!isHiddenForBuyer && !isDisabled" class="">
					<UButton
						label="Отменить изменения"
						size="lg"
						class="w-full justify-center"
						color="neutral"
						variant="subtle"
						:disabled="isDisabled"
						@click="editButton()"
					/>
				</div>

				<div v-if="!isHiddenForBuyer" class="flex flex-row justify-between">
					<UTooltip
						:text="tooltipSave"
						:disabled="!tooltipSave"
					>
						<span class="block w-full" :class="{ 'cursor-not-allowed': tooltipSave }">
							<UButton
								label="Отправить контрагенту и сохранить"
								size="xl"
								class="w-full justify-center pointer-events-auto"
								:disabled="isDisabled"
								@click="modalIsOpenSaveChanges = true"
							/>
						</span>
					</UTooltip>
				</div>
			</div>

			<!-- Сканы видны всегда (в т.ч. при согласовании изменений заказа у контрагента) -->
			<DealDocumentScans
				v-if="activeTab === '0' || activeTab === '1' || activeTab === '2'"
				:deal-id="dealIdForReview"
				:document-type="scansDocumentType"
				:read-only="isHiddenForBuyer"
				:edit-enabled="!isDisabled && !canRespondToChanges"
			/>
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
				@click="confirmSaveAndNotify"
			/>
			</div>
		</template>
	</UModal>
	<UModal
		v-model:open="updateDataModalOpen"
		title="Контрагент изменил данные заказа"
		description="Ознакомьтесь с предложенной версией заказа. Изменённые поля выделены цветом. Примите или отклоните изменения."
	>
		<template #footer>
			<UButton
				label="Позже"
				color="neutral"
				variant="outline"
				@click="dismissUpdateDataModal"
			/>
			<UButton
				label="Обновить данные"
				color="primary"
				@click="dismissUpdateDataModal"
			/>
		</template>
	</UModal>
</template>

<script setup lang="ts">
import SupplyContractMenu from "./SupplyContractMenu.vue"
import InsertButtons from "./InsertButtons.vue"
import OrderMenu from "./OrderMenu.vue"
import BillMenu from "./BillMenu.vue"
import DealDocumentScans from "./DealDocumentScans.vue"
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
import {
	useAcceptDealChangesQuery,
	useRejectDealChangesQuery,
} from "~/queries/purchases"
import { useQuery } from "@pinia/colada"
import { QueryKeys } from "~/constants/queryKeys"
import { usePurchasesApi } from "~/api/purchases"
import { normalizeDate } from "~/utils/normalize"

const modalIsOpen = ref(false)
const route = useRoute()
const router = useRouter()
const activeTab = useTypedState(Editor.ACTIVE_TAB)
const orderElement = useTypedState(TemplateElement.ORDER)
const billElement = useTypedState(TemplateElement.BILL)
const supplyContractPreviewElement = useTypedState(Editor.SUPPLY_CONTRACT_PREVIEW_ELEMENT)
const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
const billType = useTypedState(Editor.BILL_TYPE)
const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
const orderChangeDiff = useTypedState(Editor.ORDER_CHANGE_DIFF, () => ref(null))
const { createNewDealVersion, refreshDealFromServer } = useDeals()

const scansDocumentType = computed(() => {
	if (activeTab.value === "0") return "order" as const
	if (activeTab.value === "2") return "supply_contract" as const
	const selected = billType.value as { value?: string } | null | undefined
	const sub = selected?.value ?? "bill"
	if (sub === "bill-contract") return "bill_contract" as const
	if (sub === "bill-offer") return "bill_offer" as const
	return "bill" as const
})

const inDevelopment = () => {
	const toast = useToast()
	toast.add({
		title: "Кнопка находится в разработке...",
		icon: "i-lucide-git-compare"
	})
}

/** §3.3: покупатель редактирует только заказ; счёт/договор — просмотр */
const isBuyerRole = computed(() => route.query.role === "buyer")

const tooltipEdit = computed(() => {
	if (isBuyerRole.value && activeTab.value !== "0") return ""
	if (!isDisabled.value) return "Режим редактирования уже включён — поля формы активны"
	return ""
})

const tooltipPreviewExport = computed(() => {
	if (isHiddenForBuyer.value) return ""
	if (!isDisabled.value) {
		return "Печать и экспорт доступны в режиме просмотра. Сохраните изменения или нажмите «Отменить изменения»."
	}
	return ""
})

const tooltipSave = computed(() => {
	if (isHiddenForBuyer.value) return ""
	if (isDisabled.value) return "Сначала нажмите «Редактировать», чтобы изменить документ"
	return ""
})

//DOCX / PDF — с бэкенда (docxtpl + Gotenberg), см. docs/DOCX_TEMPLATES_BACKEND.md
const { downloadDealGeneratedDocx, downloadDealGeneratedPdf } = useDocxGenerator()
const isDocxDownloading = ref(false)
const isPdfDownloading = ref(false)

const handleDownloadCurrentDocx = async (tab: string): Promise<void> => {
	const dealId = Number(route.query.dealId)
	if (!dealId || Number.isNaN(dealId)) {
		useToast().add({ title: "Не выбрана сделка", color: "error" })
		return
	}
	if (isDocxDownloading.value) return
	isDocxDownloading.value = true
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
			return
		}
		if (tab === "2") {
			if (!(await persistDealBeforeExport())) return
			await downloadDealGeneratedDocx(dealId, "supply-contract")
		}
	} catch (e) {
		console.error(e)
		useToast().add({
			title: "Не удалось скачать документ",
			color: "error",
		})
	} finally {
		isDocxDownloading.value = false
	}
}

const handleDownloadCurrentPdf = async (tab: string): Promise<void> => {
	const dealId = Number(route.query.dealId)
	if (!dealId || Number.isNaN(dealId)) {
		useToast().add({ title: "Не выбрана сделка", color: "error" })
		return
	}
	if (isPdfDownloading.value) return
	isPdfDownloading.value = true
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
			return
		}
		if (tab === "2") {
			if (!(await persistDealBeforeExport())) return
			await downloadDealGeneratedPdf(dealId, "supply-contract")
		}
	} catch (e) {
		console.error(e)
		useToast().add({
			title: "Не удалось скачать PDF (нужен Gotenberg и GOTENBERG_URL на бэкенде)",
			color: "error",
		})
	} finally {
		isPdfDownloading.value = false
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
				: activeTab === "2"
					? supplyContractPreviewElement.value
					: null
	if (!root) {
		return
	}
	const cloneWithText = replaceTextareasAndInputs(root)
	const isA4Document = activeTab === "0" || activeTab === "1"
	printDocument(cloneWithText, {
		hidePageChrome: activeTab === "2",
		pageMargins: isA4Document ? "10mm" : undefined,
	})
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
				: activeTab === "2"
					? supplyContractPreviewElement.value
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
	if (isHiddenForBuyer.value) return
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

/** Сохранить сделку на сервер перед DOC/PDF — экспорт читает данные из API, не с экрана. */
const persistDealBeforeExport = async (): Promise<boolean> => {
	const dealId = Number(route.query.dealId)
	if (!dealId || Number.isNaN(dealId) || route.query.role !== "seller") {
		return true
	}
	try {
		await startSave()
		await createNewDealVersion(dealId)
		await refreshDealFromServer(dealId)
		loadDealTrigger.value++
		return true
	} catch (err) {
		console.error("persistDealBeforeExport:", err)
		useToast().add({
			title: "Не удалось сохранить перед экспортом",
			description: "Сначала нажмите «Отправить контрагенту и сохранить»",
			color: "error",
		})
		return false
	}
}


const counterpartData: CounterpartData | null = getCounterpartData(
	Number(route.query.dealId),
	route.query.role as "buyer" | "seller"
)

const saveDealVersion = async (): Promise<void> => {
	const dealId = Number(route.query.dealId)
	await startSave()
	await createNewDealVersion(dealId)
	const ok = await refreshDealFromServer(dealId)
	if (ok) {
		loadDealTrigger.value++
	}
	editButton()
}

const confirmSaveAndNotify = async (): Promise<void> => {
	modalIsOpenSaveChanges.value = false
	const dealId = Number(route.query.dealId)
	const role = route.query.role as "buyer" | "seller"

	try {
		await saveDealVersion()
	} catch (err) {
		console.error("Ошибка при сохранении версии сделки:", err)
		useToast().add({
			title: "Не удалось сохранить изменения сделки",
			color: "error",
		})
		return
	}

	if (!counterpartData?.companyId) {
		useToast().add({
			title: "Изменения сохранены",
			color: "success",
		})
		return
	}

	try {
		await sendMessageToCounterpart(dealId, role, counterpartData)
		useToast().add({
			title: "Изменения сохранены и отправлены контрагенту",
			color: "success",
		})
		void refetchChangeReview()
	} catch (err) {
		console.error("Ошибка при отправке сообщения контрагенту:", err)
		useToast().add({
			title: "Изменения сохранены, но уведомление в чат не отправлено",
			color: "warning",
		})
	}
}

// cancel button — ранее переключал «последняя закупка/продажа»; §1.3 убрано

// Согласование изменений заказа — по API, не только по query confirmation=
const dealIdForReview = computed(() => Number(route.query.dealId) || 0)

const { data: changeReview, refetch: refetchChangeReview } = useQuery({
	key: () => [QueryKeys.DEAL_CHANGE_REVIEW, dealIdForReview.value],
	query: () => usePurchasesApi().getDealChangeReview(dealIdForReview.value),
	enabled: () => dealIdForReview.value > 0,
})

const canRespondToChanges = computed(() => changeReview.value?.can_respond === true)

const BILL_TYPE_LABELS: Record<string, string> = {
	bill: 'Счет на оплату',
	'bill-contract': 'Счет-договор',
	'bill-offer': 'Счет-оферта',
}

const billTypeChangeSummary = computed(() => {
	const diff = changeReview.value?.diff
	if (!diff?.bill_document_type_changed) return ''
	const before = BILL_TYPE_LABELS[diff.bill_document_type_before ?? 'bill']
		?? diff.bill_document_type_before
	const after = BILL_TYPE_LABELS[diff.bill_document_type_after ?? 'bill']
		?? diff.bill_document_type_after
	return `Изменён тип счёта: «${before}» → «${after}».`
})

const billDateChangeSummary = computed(() => {
	const diff = changeReview.value?.diff
	if (!diff?.bill_date_changed) return ''
	const before = normalizeDate(diff.bill_date_before || '') || '—'
	const after = normalizeDate(diff.bill_date_after || '') || '—'
	return `Изменена дата счёта: «${before}» → «${after}».`
})

const hasOrderVisualDiff = computed(() => {
	const diff = changeReview.value?.diff
	if (!diff) return false
	return Boolean(
		diff.items?.length
		|| diff.comments_changed
		|| diff.total_amount_changed
		|| diff.bill_date_changed
		|| diff.bill_document_type_changed,
	)
})

const isHiddenForBuyer = computed(() => {
	if (!isBuyerRole.value) return false
	if (canRespondToChanges.value) return true
	return activeTab.value !== "0"
})

const updateDataModalOpen = ref(false)
const updateDataModalDismissedForVersion = ref<number | null>(null)

watch(
	() => [canRespondToChanges.value, changeReview.value?.version] as const,
	([canRespond, version]) => {
		if (!canRespond || version == null) return
		if (updateDataModalDismissedForVersion.value === version) return
		updateDataModalOpen.value = true
	},
	{ immediate: true },
)

const dismissUpdateDataModal = () => {
	updateDataModalOpen.value = false
	if (changeReview.value?.version != null) {
		updateDataModalDismissedForVersion.value = changeReview.value.version
	}
}

const pendingReviewHint = computed(
	() =>
		Boolean(changeReview.value?.has_pending_changes && changeReview.value?.is_proposer)
)

let changeReviewPollTimer: ReturnType<typeof setInterval> | null = null

watch(dealIdForReview, (id) => {
	if (id > 0) {
		void refetchChangeReview()
	}
})

onMounted(() => {
	changeReviewPollTimer = setInterval(() => {
		if (dealIdForReview.value > 0) {
			void refetchChangeReview()
		}
	}, 15000)
})

onUnmounted(() => {
	if (changeReviewPollTimer) {
		clearInterval(changeReviewPollTimer)
	}
})

/** При pending-изменениях подтягиваем latest-версию с API в форму заказа. */
const lastSyncedReviewKey = ref("")

watch(
	() => changeReview.value,
	async (review) => {
		const dealId = dealIdForReview.value
		if (!dealId || !review) return

		orderChangeDiff.value =
			review.has_pending_changes && review.diff ? review.diff : null

		const reviewKey = `${review.has_pending_changes}:${review.version}`
		if (reviewKey === lastSyncedReviewKey.value) return

		const wasPending = lastSyncedReviewKey.value.startsWith("true:")
		const shouldSync = review.has_pending_changes || wasPending
		lastSyncedReviewKey.value = reviewKey

		if (!shouldSync) return

		const ok = await refreshDealFromServer(dealId)
		if (ok) {
			loadDealTrigger.value++
		}
	},
	{ immediate: true },
)

const { acceptDealChangesAsync } = useAcceptDealChangesQuery()
const { rejectDealChangesAsync } = useRejectDealChangesQuery()
const changeReviewActionLoading = ref(false)

const confirm = async () => {
	const dealId = Number(route.query.dealId)
	const role = route.query.role as "buyer" | "seller"
	if (!dealId) return

	changeReviewActionLoading.value = true
	try {
		await acceptDealChangesAsync(dealId)
		loadDealTrigger.value++
		await refetchChangeReview()
		if (counterpartData?.companyId) {
			await sendMessageToCounterpart(dealId, role, counterpartData, true)
		}
		useToast().add({
			title: "Изменения приняты",
			color: "success",
		})
	} catch (err) {
		console.error("Ошибка при принятии изменений:", err)
		useToast().add({
			title: "Не удалось принять изменения",
			color: "error",
		})
	} finally {
		changeReviewActionLoading.value = false
		if (route.query.confirmation === "true") {
			const { confirmation: _removed, ...restQuery } = route.query
			router.replace({ query: restQuery })
		}
	}
}

const reject = async () => {
	const dealId = Number(route.query.dealId)
	const role = route.query.role as "buyer" | "seller"
	if (!dealId) return

	changeReviewActionLoading.value = true
	try {
		await rejectDealChangesAsync(dealId)
		await refreshDealFromServer(dealId)
		loadDealTrigger.value++
		await refetchChangeReview()
		if (counterpartData?.companyId) {
			await sendMessageToCounterpart(dealId, role, counterpartData, false)
		}
		useToast().add({
			title: "Изменения отклонены",
			color: "warning",
		})
	} catch (err) {
		console.error("Ошибка при отклонении изменений:", err)
		useToast().add({
			title: "Не удалось отклонить изменения",
			color: "error",
		})
	} finally {
		changeReviewActionLoading.value = false
		if (route.query.confirmation === "true") {
			const { confirmation: _removed, ...restQuery } = route.query
			router.replace({ query: restQuery })
		}
	}
}
</script>

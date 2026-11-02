import { useRouter } from 'vue-router'
import { useDeals } from '~/composables/useDeals'
import { usePurchasesApi } from '~/api/purchases'
import { Editor } from '~/constants/keys'
import {
	TRANSPORT_DOCUMENT_TYPES,
	TRANSPORT_DOCUMENT_TYPE_LABELS,
	type TransportDocumentType,
} from '~/types/transportDocument'
import { resolveTransportDocFlow } from '~/utils/transportDocumentFlow'
import { shortenOrgName } from '~/utils/transportDocumentLabels'

const isTypeModalOpen = ref(false)
const isAlertModalOpen = ref(false)
const isPickerModalOpen = ref(false)
const isBusy = ref(false)

const pendingDealNumber = ref('')
const pendingDealId = ref<number | null>(null)
const selectedDocType = ref<TransportDocumentType | null>(null)

const alertTitle = ref('')
const alertMessage = ref('')
const alertBackTo = ref<'type_select' | 'close'>('close')

const pickerShowContracts = ref(true)
const carriers = ref<{ id: number; name: string }[]>([])
const selectedCarrierId = ref<number | undefined>()
const contracts = ref<{ id: number; number: string; date: string }[]>([])
const selectedContractId = ref<number | undefined>()

/**
 * Диалог «Создать документ» в колонке «Договор перевозки» (§1.3).
 */
export function useCreateTransportDocumentFromSales() {
	const router = useRouter()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const { findDeal, findDealByDealNumber, updateDeal } = useDeals()
	const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
	const activeTab = useTypedState(Editor.ACTIVE_TAB, () => ref('0'))

	const typeRadioItems = TRANSPORT_DOCUMENT_TYPES.map((value) => ({
		value,
		label: TRANSPORT_DOCUMENT_TYPE_LABELS[value],
	}))

	const carrierSelectItems = computed(() =>
		carriers.value.map((c) => ({
			label: shortenOrgName(c.name),
			value: String(c.id),
		})),
	)

	const contractSelectItems = computed(() =>
		contracts.value.map((c) => ({
			label: `№ ${c.number}`,
			value: String(c.id),
		})),
	)

	const pickerCanChoose = computed(
		() => Boolean(selectedCarrierId.value) && !isBusy.value,
	)
	const pickerCanBind = computed(
		() =>
			pickerCanChoose.value &&
			pickerShowContracts.value &&
			Boolean(selectedContractId.value),
	)

	const resetPicker = () => {
		selectedCarrierId.value = undefined
		selectedContractId.value = undefined
		contracts.value = []
	}

	const closeAll = () => {
		isTypeModalOpen.value = false
		isAlertModalOpen.value = false
		isPickerModalOpen.value = false
		pendingDealNumber.value = ''
		pendingDealId.value = null
		selectedDocType.value = null
		resetPicker()
	}

	const openTypeSelect = (dealNumber: string) => {
		const deal = findDealByDealNumber(dealNumber, 'seller')
		if (!deal?.dealId) {
			toast.add({ title: 'Сделка не найдена', color: 'error' })
			return
		}
		pendingDealNumber.value = dealNumber
		pendingDealId.value = deal.dealId
		selectedDocType.value = null
		isAlertModalOpen.value = false
		isPickerModalOpen.value = false
		isTypeModalOpen.value = true
	}

	const showAlert = (
		title: string,
		message: string,
		backTo: 'type_select' | 'close',
	) => {
		alertTitle.value = title
		alertMessage.value = message
		alertBackTo.value = backTo
		isTypeModalOpen.value = false
		isPickerModalOpen.value = false
		isAlertModalOpen.value = true
	}

	const refreshDealLocal = async (dealId: number) => {
		updateDeal(dealId)
		loadDealTrigger.value++
		try {
			const listed = await purchasesApi.listDealTransportDocuments(dealId)
			const deal = findDeal(dealId)
			if (!deal) return
			const documents = (listed.documents ?? []).map((d) => ({
				id: d.id,
				type: d.doc_type,
				number: d.number,
				date: d.date,
				carrier_company_id: d.carrier_company_id,
				carrier_name: d.carrier_name,
				parent_id: d.parent_id ?? null,
			}))
			const primary =
				documents.find((d) =>
					['carriage_contract', 'expedition_contract', 'carriage_order'].includes(
						String(d.type),
					),
				) ?? documents[0]
			deal.transportContract = {
				...(deal.transportContract ?? {}),
				documents,
				number: primary?.number,
				date: primary?.date,
				type: primary?.type,
				carrier_company_id: primary?.carrier_company_id,
				carrier_name: primary?.carrier_name,
			}
		} catch {
			/* локальный refresh лучший effort */
		}
	}

	const openEditorForTransport = async (
		dealId: number,
		docType: TransportDocumentType,
		documentId?: number,
	) => {
		activeTab.value = '5'
		loadDealTrigger.value++
		await router.replace({
			path: '/profile/editor',
			query: {
				dealId: String(dealId),
				role: 'seller',
				transportDocType: docType,
				...(documentId ? { transportDocId: String(documentId) } : {}),
			},
			hash: '#contract',
		})
	}

	const createChildOnDeal = async (
		docType: TransportDocumentType,
		parentId: number,
		carrierCompanyId: number,
	) => {
		const dealId = pendingDealId.value
		if (!dealId) return
		isBusy.value = true
		try {
			const created = await purchasesApi.createTransportDocument({
				doc_type: docType,
				carrier_company_id: carrierCompanyId,
				parent_id: parentId,
				deal_id: dealId,
			})
			await purchasesApi.bindTransportDocument(dealId, created.id)
			await refreshDealLocal(dealId)
			closeAll()
			toast.add({
				title: 'Документ создан',
				description: `${TRANSPORT_DOCUMENT_TYPE_LABELS[docType]} № ${created.number}`,
				color: 'success',
			})
			await openEditorForTransport(dealId, docType, created.id)
		} catch {
			toast.add({ title: 'Не удалось создать документ', color: 'error' })
		} finally {
			isBusy.value = false
		}
	}

	const confirmTypeSelect = async () => {
		const docType = selectedDocType.value
		const dealId = pendingDealId.value
		if (!docType || !dealId) return

		isBusy.value = true
		try {
			const deal = findDeal(dealId)
			const carrierList = await purchasesApi.listMyCarriers()
			carriers.value = carrierList
			const flow = resolveTransportDocFlow({
				docType,
				carriersCount: carrierList.length,
				dealTransport: deal?.transportContract ?? null,
			})

			if (flow.step === 'alert') {
				showAlert(flow.title, flow.message, flow.backTo)
				return
			}

			if (flow.step === 'create_child') {
				const parentDoc = (deal?.transportContract?.documents ?? []).find(
					(d) => d.id === flow.parentId,
				)
				const carrierId =
					parentDoc?.carrier_company_id ??
					deal?.transportContract?.carrier_company_id
				if (!carrierId) {
					showAlert(
						TRANSPORT_DOCUMENT_TYPE_LABELS[docType],
						'Не удалось определить перевозчика у договора на заказе',
						'type_select',
					)
					return
				}
				await createChildOnDeal(docType, flow.parentId, carrierId)
				return
			}

			if (flow.step === 'org_contracts_picker') {
				pickerShowContracts.value = flow.showContracts
				resetPicker()
				isTypeModalOpen.value = false
				isPickerModalOpen.value = true
			}
		} catch {
			toast.add({ title: 'Ошибка загрузки перевозчиков', color: 'error' })
		} finally {
			isBusy.value = false
		}
	}

	const onCarrierChange = async (value: unknown) => {
		const id = value ? Number(value) : undefined
		selectedCarrierId.value = id
		selectedContractId.value = undefined
		contracts.value = []
		if (!id || !selectedDocType.value || !pickerShowContracts.value) return
		if (
			selectedDocType.value !== 'carriage_contract' &&
			selectedDocType.value !== 'expedition_contract'
		) {
			return
		}
		isBusy.value = true
		try {
			const listed = await purchasesApi.listTransportDocuments(
				id,
				selectedDocType.value,
			)
			contracts.value = (listed.documents ?? []).map((d) => ({
				id: d.id,
				number: d.number,
				date: d.date,
			}))
		} catch {
			toast.add({ title: 'Не удалось загрузить договоры', color: 'error' })
		} finally {
			isBusy.value = false
		}
	}

	const bindSelectedContract = async () => {
		const dealId = pendingDealId.value
		const contractId = selectedContractId.value
		if (!dealId || !contractId) return
		isBusy.value = true
		try {
			await purchasesApi.bindTransportDocument(dealId, contractId)
			await refreshDealLocal(dealId)
			closeAll()
			toast.add({ title: 'Договор привязан к заказу', color: 'success' })
		} catch {
			toast.add({ title: 'Не удалось привязать договор', color: 'error' })
		} finally {
			isBusy.value = false
		}
	}

	const createNewFromPicker = async () => {
		const dealId = pendingDealId.value
		const carrierId = selectedCarrierId.value
		const docType = selectedDocType.value
		if (!dealId || !carrierId || !docType) return
		isBusy.value = true
		try {
			const created = await purchasesApi.createTransportDocument({
				doc_type: docType,
				carrier_company_id: carrierId,
				deal_id: dealId,
			})
			await purchasesApi.bindTransportDocument(dealId, created.id)
			await refreshDealLocal(dealId)
			closeAll()
			toast.add({
				title: 'Документ создан',
				description: `№ ${created.number}`,
				color: 'success',
			})
			await openEditorForTransport(dealId, docType, created.id)
		} catch {
			toast.add({ title: 'Не удалось создать документ', color: 'error' })
		} finally {
			isBusy.value = false
		}
	}

	const confirmAlert = () => {
		isAlertModalOpen.value = false
		if (alertBackTo.value === 'type_select') {
			isTypeModalOpen.value = true
			return
		}
		closeAll()
	}

	const backFromPickerToTypes = () => {
		isPickerModalOpen.value = false
		resetPicker()
		isTypeModalOpen.value = true
	}

	return {
		isTypeModalOpen,
		isAlertModalOpen,
		isPickerModalOpen,
		isBusy,
		selectedDocType,
		typeRadioItems,
		alertTitle,
		alertMessage,
		pickerShowContracts,
		carrierSelectItems,
		contractSelectItems,
		selectedCarrierId,
		selectedContractId,
		pickerCanChoose,
		pickerCanBind,
		openTypeSelect,
		confirmTypeSelect,
		confirmAlert,
		onCarrierChange,
		bindSelectedContract,
		createNewFromPicker,
		backFromPickerToTypes,
		closeAll,
	}
}

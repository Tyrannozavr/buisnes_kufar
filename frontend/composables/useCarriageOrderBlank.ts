import { Editor } from '~/constants/keys'
import {
	CARRIAGE_ORDER_INTRO,
	DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS,
	emptyCarriageOrderPayload,
	type CarriageOrderPayload,
} from '~/utils/carriageOrderDefaults'
import {
	emptyCarriageParty,
	type CarriagePartyPayload,
} from '~/utils/carriageContractDefaults'
import {
	buildCargoTransportTableRows,
	rowsToSnapshot,
	type CargoTransportTableRow,
} from '~/utils/cargoTransportTable'
import { partyFromCompany, RED_READONLY_CLASS, YELLOW_INPUT_CLASS } from '~/utils/carriageParty'
import { usePurchasesApi } from '~/api/purchases'
import { useTransportApi } from '~/api/transport'
import { useDeals } from '~/composables/useDeals'
import { getMyCompany } from '~/api/companyOwner'
import { useCompaniesApi } from '~/api/companies'
import type { CargoData } from '~/types/transport'

const documentId = ref<number | null>(null)
const number = ref('')
const dateIso = ref('')
const city = ref('')
const preambleDate = ref('')
const customer = ref<CarriagePartyPayload>(emptyCarriageParty())
const carrier = ref<CarriagePartyPayload>(emptyCarriageParty())
const extraTermsHtml = ref(DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS)
const customerDetailsCheck = ref(true)
const carrierDetailsCheck = ref(true)
const tableRows = ref<CargoTransportTableRow[]>([])
const shipmentId = ref<number | null>(null)
const loading = ref(false)
const saving = ref(false)

export function useCarriageOrderBlank() {
	const route = useRoute()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const transportApi = useTransportApi()
	const { findDeal } = useDeals()
	const { getCompanyById } = useCompaniesApi()
	const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
	const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
	const slotRevision = useTypedState(Editor.CARRIAGE_ORDER_SLOT_REVISION, () => ref(0))

	const dealId = computed(() => Number(route.query.dealId) || 0)
	const currentDeal = computed(() => findDeal(dealId.value))
	const isOrderDoc = computed(
		() => String(route.query.transportDocType || '') === 'carriage_order',
	)

	const bumpSlot = () => {
		slotRevision.value += 1
	}

	const resolveDocumentId = (): number | null => {
		const fromQuery = Number(route.query.transportDocId)
		if (Number.isFinite(fromQuery) && fromQuery > 0) return fromQuery
		const docs = currentDeal.value?.transportContract?.documents ?? []
		const match =
			docs.find((d) => d.type === 'carriage_order' && d.id) ||
			docs.find((d) => d.id)
		return match?.id ? Number(match.id) : null
	}

	const applyPayload = (payload: CarriageOrderPayload | null | undefined) => {
		if (!payload) {
			const empty = emptyCarriageOrderPayload()
			city.value = empty.city
			preambleDate.value = empty.preambleDate
			customer.value = empty.customer
			carrier.value = empty.carrier
			extraTermsHtml.value = empty.extraTermsHtml
			customerDetailsCheck.value = true
			carrierDetailsCheck.value = true
			return
		}
		city.value = payload.city || ''
		preambleDate.value = payload.preambleDate || ''
		customer.value = { ...emptyCarriageParty(), ...(payload.customer || {}) }
		carrier.value = { ...emptyCarriageParty(), ...(payload.carrier || {}) }
		extraTermsHtml.value =
			payload.extraTermsHtml || DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS
		customerDetailsCheck.value = payload.customerDetailsCheck !== false
		carrierDetailsCheck.value = payload.carrierDetailsCheck !== false
		if (payload.cargoTableSnapshot && typeof payload.cargoTableSnapshot === 'object') {
			tableRows.value = Object.entries(payload.cargoTableSnapshot).map(
				([label, value]) => ({ label, value: String(value ?? '') }),
			)
		}
	}

	const loadShipmentCargo = async (): Promise<void> => {
		shipmentId.value = null
		if (!dealId.value) {
			tableRows.value = buildCargoTransportTableRows(null, null)
			return
		}
		try {
			const list = await transportApi.listShipments({ deal_id: dealId.value })
			const shipment = (list || [])[0]
			if (!shipment?.id) {
				tableRows.value = buildCargoTransportTableRows(null, null)
				return
			}
			shipmentId.value = shipment.id
			const [cargoRes, transportRes] = await Promise.all([
				transportApi.getCargo(shipment.id),
				transportApi.getTransport(shipment.id),
			])
			const cargo = (cargoRes?.cargo_data || null) as CargoData | null
			const snap = (transportRes?.transport_snapshot || null) as Record<
				string,
				unknown
			> | null
			tableRows.value = buildCargoTransportTableRows(cargo, snap)
		} catch {
			tableRows.value = buildCargoTransportTableRows(null, null)
		}
	}

	const loadDocument = async () => {
		const id = resolveDocumentId()
		documentId.value = id
		if (!id) {
			tableRows.value = []
			bumpSlot()
			return
		}
		loading.value = true
		try {
			const doc = await purchasesApi.getTransportDocument(id)
			number.value = doc.number || ''
			dateIso.value = doc.date ? String(doc.date).slice(0, 10) : ''
			applyPayload(doc.payload_json as CarriageOrderPayload | undefined)
			if (!preambleDate.value) preambleDate.value = dateIso.value
			await loadShipmentCargo()
			bumpSlot()
		} catch (e: any) {
			toast.add({
				title: 'Не удалось загрузить договор-заявку',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const buildPayload = (): CarriageOrderPayload => ({
		city: city.value,
		preambleDate: preambleDate.value,
		customer: { ...customer.value },
		carrier: { ...carrier.value },
		extraTermsHtml: extraTermsHtml.value,
		customerDetailsCheck: customerDetailsCheck.value,
		carrierDetailsCheck: carrierDetailsCheck.value,
		cargoTableSnapshot: rowsToSnapshot(tableRows.value),
	})

	const saveDocument = async (opts?: { silent?: boolean }): Promise<boolean> => {
		if (!documentId.value) {
			toast.add({ title: 'Договор-заявка не выбран', color: 'warning' })
			return false
		}
		saving.value = true
		try {
			const updated = await purchasesApi.updateTransportDocument(documentId.value, {
				payload_json: buildPayload() as unknown as Record<string, unknown>,
			})
			number.value = updated.number
			dateIso.value = updated.date ? String(updated.date).slice(0, 10) : dateIso.value
			if (!opts?.silent) {
				toast.add({ title: 'Договор-заявка сохранён', color: 'success' })
			}
			bumpSlot()
			return true
		} catch (e: any) {
			toast.add({
				title: 'Не удалось сохранить договор-заявку',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
			return false
		} finally {
			saving.value = false
		}
	}

	const fillFromLk = async () => {
		if (!documentId.value) {
			toast.add({ title: 'Договор-заявка не выбран', color: 'warning' })
			return
		}
		loading.value = true
		try {
			const doc = await purchasesApi.getTransportDocument(documentId.value)
			const owner = await getMyCompany()
			let carrierCompany: Record<string, any> | null = null
			try {
				carrierCompany = (await getCompanyById(doc.carrier_company_id, false)) as Record<
					string,
					any
				>
			} catch {
				carrierCompany = null
			}
			customer.value = partyFromCompany(owner as Record<string, any>)
			carrier.value = partyFromCompany(carrierCompany)
			if (!city.value) city.value = customer.value.city || city.value
			if (!preambleDate.value) preambleDate.value = dateIso.value
			if (!extraTermsHtml.value?.trim()) {
				extraTermsHtml.value = DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS
			}
			await loadShipmentCargo()
			bumpSlot()
			const saved = await saveDocument({ silent: true })
			toast.add({
				title: saved
					? 'Данные из ЛК и перевозки подставлены и сохранены'
					: 'Данные подставлены, но не сохранены',
				color: saved ? 'success' : 'warning',
			})
		} catch (e: any) {
			toast.add({
				title: 'Не удалось заполнить',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const refreshCargoTable = async () => {
		await loadShipmentCargo()
		bumpSlot()
		toast.add({ title: 'Таблица перевозки обновлена', color: 'success' })
	}

	const resetBlank = () => {
		const empty = emptyCarriageOrderPayload()
		city.value = empty.city
		preambleDate.value = empty.preambleDate
		customer.value = empty.customer
		carrier.value = empty.carrier
		extraTermsHtml.value = empty.extraTermsHtml
		customerDetailsCheck.value = true
		carrierDetailsCheck.value = true
		tableRows.value = buildCargoTransportTableRows(null, null)
		bumpSlot()
	}

	const applyDefaultExtraTerms = () => {
		extraTermsHtml.value = DEFAULT_CARRIAGE_ORDER_EXTRA_TERMS
		bumpSlot()
	}

	return {
		documentId,
		number,
		dateIso,
		city,
		preambleDate,
		customer,
		carrier,
		extraTermsHtml,
		customerDetailsCheck,
		carrierDetailsCheck,
		tableRows,
		shipmentId,
		loading,
		saving,
		isDisabled,
		dealId,
		currentDeal,
		loadDealTrigger,
		slotRevision,
		isOrderDoc,
		introStatic: CARRIAGE_ORDER_INTRO,
		yellowInputClass: YELLOW_INPUT_CLASS,
		redReadonlyClass: RED_READONLY_CLASS,
		loadDocument,
		saveDocument,
		fillFromLk,
		refreshCargoTable,
		resetBlank,
		applyDefaultExtraTerms,
		bumpSlot,
	}
}

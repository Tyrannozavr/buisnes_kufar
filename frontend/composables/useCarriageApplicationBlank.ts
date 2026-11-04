import { Editor } from '~/constants/keys'
import {
	DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS,
	emptyCarriageApplicationPayload,
	emptyCarriageParty,
	type CarriageApplicationPayload,
	type CarriagePartyPayload,
} from '~/utils/carriageApplicationDefaults'
import {
	buildCargoTransportTableRows,
	rowsToSnapshot,
	type CargoTransportTableRow,
} from '~/utils/cargoTransportTable'
import { usePurchasesApi } from '~/api/purchases'
import { useTransportApi } from '~/api/transport'
import { useDeals } from '~/composables/useDeals'
import { getMyCompany } from '~/api/companyOwner'
import { useCompaniesApi } from '~/api/companies'
import {
	formatCompanyRecipientLine,
	formatLegalAddressForParty,
} from '~/utils/companyPartyLine'
import type { CargoData } from '~/types/transport'

const legalPartyName = (company: Record<string, any>): string => {
	const companyType = String(company.type || company.company_type || '')
	const raw = String(company.full_name || company.fullName || company.name || '')
	if (/общество с ограниченной ответственностью/i.test(raw)) return raw
	if (/индивидуальный предприниматель/i.test(raw)) return raw
	if (/акционерное общество/i.test(raw)) return raw
	return formatCompanyRecipientLine({ companyType, companyName: raw }) || raw
}

const foundationFromOfficial = (official: Record<string, any>) => {
	const rawKind = String(official.base_document || official.baseDocument || '').trim()
	const rawTitle = String(
		official.base_document_name || official.baseDocumentName || '',
	).trim()
	let foundationKind = rawKind || 'Устава'
	if (/^устав$/i.test(foundationKind)) foundationKind = 'Устава'
	if (/^доверенность$/i.test(foundationKind)) foundationKind = 'доверенности'
	const kindStem = foundationKind.replace(/а$/i, '').toLowerCase()
	const titleLooksSame =
		!rawTitle ||
		rawTitle.toLowerCase() === rawKind.toLowerCase() ||
		rawTitle.toLowerCase() === foundationKind.toLowerCase() ||
		rawTitle.toLowerCase() === kindStem ||
		/^устав$/i.test(rawTitle)
	return {
		foundationKind,
		foundationTitle: titleLooksSame ? '' : rawTitle,
	}
}

const partyFromCompany = (company: Record<string, any> | null | undefined): CarriagePartyPayload => {
	if (!company) return emptyCarriageParty()
	const officials = (company.officials ?? []) as Array<Record<string, any>>
	const first = officials[0] ?? {}
	const companyType = String(company.type || company.company_type || '')
	const index = String(company.index || '')
	const legalRaw = String(company.legal_address || company.legalAddress || '')
	const foundation = foundationFromOfficial(first)
	return {
		fullName: legalPartyName(company),
		companyType,
		city: String(company.city || ''),
		index,
		legalAddress: formatLegalAddressForParty(index, legalRaw),
		inn: String(company.inn ?? ''),
		kpp: String(company.kpp ?? ''),
		ogrn: String(company.ogrn ?? ''),
		accountNumber: String(company.current_account_number || company.accountNumber || ''),
		bankName: String(company.bank_name || company.bankName || ''),
		correspondentBankAccount: String(
			company.correspondent_bank_account || company.correspondentBankAccount || '',
		),
		bic: String(company.bic || ''),
		officialPosition: String(first.position || first.job_title || 'Генеральный директор'),
		officialName: String(first.name || first.full_name || ''),
		foundationKind: foundation.foundationKind,
		foundationTitle: foundation.foundationTitle,
	}
}

const documentId = ref<number | null>(null)
const number = ref('')
const dateIso = ref('')
const parentId = ref<number | null>(null)
const parentNumber = ref('')
const parentDateIso = ref('')
const customer = ref<CarriagePartyPayload>(emptyCarriageParty())
const carrier = ref<CarriagePartyPayload>(emptyCarriageParty())
const extraTermsHtml = ref(DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS)
const customerDetailsCheck = ref(true)
const carrierDetailsCheck = ref(true)
const tableRows = ref<CargoTransportTableRow[]>([])
const shipmentId = ref<number | null>(null)
const loading = ref(false)
const saving = ref(false)

const yellowInputClass =
	'bg-yellow-100 border border-yellow-300 rounded px-1 min-w-[5rem] min-h-[1.5rem] disabled:opacity-80'

/** Красные поля шапки — только чтение на А4 (§3.1). */
const redReadonlyClass =
	'text-red-600 font-semibold bg-transparent border-0 border-b border-red-300 px-1 min-w-[3rem] text-center cursor-default'

export function useCarriageApplicationBlank() {
	const route = useRoute()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const transportApi = useTransportApi()
	const { findDeal } = useDeals()
	const { getCompanyById } = useCompaniesApi()
	const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
	const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
	const slotRevision = useTypedState(Editor.CARRIAGE_APPLICATION_SLOT_REVISION, () => ref(0))

	const dealId = computed(() => Number(route.query.dealId) || 0)
	const currentDeal = computed(() => findDeal(dealId.value))
	const isApplicationDoc = computed(
		() => String(route.query.transportDocType || '') === 'carriage_application',
	)

	const bumpSlot = () => {
		slotRevision.value += 1
	}

	const resolveDocumentId = (): number | null => {
		const fromQuery = Number(route.query.transportDocId)
		if (Number.isFinite(fromQuery) && fromQuery > 0) return fromQuery
		const docs = currentDeal.value?.transportContract?.documents ?? []
		const match =
			docs.find((d) => d.type === 'carriage_application' && d.id) ||
			docs.find((d) => d.id)
		return match?.id ? Number(match.id) : null
	}

	const applyPayload = (payload: CarriageApplicationPayload | null | undefined) => {
		if (!payload) {
			customer.value = emptyCarriageParty()
			carrier.value = emptyCarriageParty()
			extraTermsHtml.value = DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS
			customerDetailsCheck.value = true
			carrierDetailsCheck.value = true
			return
		}
		customer.value = { ...emptyCarriageParty(), ...(payload.customer || {}) }
		carrier.value = { ...emptyCarriageParty(), ...(payload.carrier || {}) }
		extraTermsHtml.value =
			payload.extraTermsHtml || DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS
		customerDetailsCheck.value = payload.customerDetailsCheck !== false
		carrierDetailsCheck.value = payload.carrierDetailsCheck !== false
		if (payload.cargoTableSnapshot && typeof payload.cargoTableSnapshot === 'object') {
			tableRows.value = Object.entries(payload.cargoTableSnapshot).map(
				([label, value]) => ({ label, value: String(value ?? '') }),
			)
		}
	}

	const loadParent = async (pid: number | null | undefined) => {
		parentId.value = pid && pid > 0 ? pid : null
		parentNumber.value = ''
		parentDateIso.value = ''
		if (!parentId.value) return
		try {
			const parent = await purchasesApi.getTransportDocument(parentId.value)
			parentNumber.value = parent.number || ''
			parentDateIso.value = parent.date ? String(parent.date).slice(0, 10) : ''
		} catch {
			parentNumber.value = ''
			parentDateIso.value = ''
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
			await loadParent(null)
			tableRows.value = []
			bumpSlot()
			return
		}
		loading.value = true
		try {
			const doc = await purchasesApi.getTransportDocument(id)
			number.value = doc.number || ''
			dateIso.value = doc.date ? String(doc.date).slice(0, 10) : ''
			applyPayload(doc.payload_json as CarriageApplicationPayload | undefined)
			await Promise.all([loadParent(doc.parent_id), loadShipmentCargo()])
			bumpSlot()
		} catch (e: any) {
			toast.add({
				title: 'Не удалось загрузить заявку',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const buildPayload = (): CarriageApplicationPayload => ({
		customer: { ...customer.value },
		carrier: { ...carrier.value },
		extraTermsHtml: extraTermsHtml.value,
		customerDetailsCheck: customerDetailsCheck.value,
		carrierDetailsCheck: carrierDetailsCheck.value,
		cargoTableSnapshot: rowsToSnapshot(tableRows.value),
	})

	const saveDocument = async (opts?: { silent?: boolean }): Promise<boolean> => {
		if (!documentId.value) {
			toast.add({ title: 'Заявка не выбрана', color: 'warning' })
			return false
		}
		saving.value = true
		try {
			const updated = await purchasesApi.updateTransportDocument(documentId.value, {
				// номер/дата заявки системные — не меняем с А4
				payload_json: buildPayload() as unknown as Record<string, unknown>,
			})
			number.value = updated.number
			dateIso.value = updated.date ? String(updated.date).slice(0, 10) : dateIso.value
			if (!opts?.silent) {
				toast.add({ title: 'Заявка сохранена', color: 'success' })
			}
			bumpSlot()
			return true
		} catch (e: any) {
			toast.add({
				title: 'Не удалось сохранить заявку',
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
			toast.add({ title: 'Заявка не выбрана', color: 'warning' })
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
			if (!extraTermsHtml.value?.trim()) {
				extraTermsHtml.value = DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS
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
		const empty = emptyCarriageApplicationPayload()
		customer.value = empty.customer
		carrier.value = empty.carrier
		extraTermsHtml.value = empty.extraTermsHtml
		customerDetailsCheck.value = true
		carrierDetailsCheck.value = true
		tableRows.value = buildCargoTransportTableRows(null, null)
		bumpSlot()
	}

	const applyDefaultExtraTerms = () => {
		extraTermsHtml.value = DEFAULT_CARRIAGE_APPLICATION_EXTRA_TERMS
		bumpSlot()
	}

	return {
		documentId,
		number,
		dateIso,
		parentId,
		parentNumber,
		parentDateIso,
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
		isApplicationDoc,
		loadDealTrigger,
		slotRevision,
		yellowInputClass,
		redReadonlyClass,
		loadDocument,
		saveDocument,
		fillFromLk,
		refreshCargoTable,
		buildPayload,
		resolveDocumentId,
		resetBlank,
		applyDefaultExtraTerms,
		bumpSlot,
	}
}

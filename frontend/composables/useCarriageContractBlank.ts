import { Editor } from '~/constants/keys'
import {
	DEFAULT_CARRIAGE_CONTRACT_BODY,
	emptyCarriageParty,
	type CarriageContractPayload,
	type CarriagePartyPayload,
} from '~/utils/carriageContractDefaults'
import { usePurchasesApi } from '~/api/purchases'
import { useDeals } from '~/composables/useDeals'
import { getMyCompany } from '~/api/companyOwner'
import { useCompaniesApi } from '~/api/companies'
import {
	formatCompanyRecipientLine,
	formatLegalAddressForParty,
} from '~/utils/companyPartyLine'

/** Полное юр. название без «ООО» + «Общество с ограниченной…». */
const legalPartyName = (company: Record<string, any>): string => {
	const companyType = String(company.type || company.company_type || '')
	const raw = String(company.full_name || company.fullName || company.name || '')
	if (/общество с ограниченной ответственностью/i.test(raw)) return raw
	if (/индивидуальный предприниматель/i.test(raw)) return raw
	if (/акционерное общество/i.test(raw)) return raw
	return (
		formatCompanyRecipientLine({ companyType, companyName: raw }) || raw
	)
}

const documentId = ref<number | null>(null)
const number = ref('')
const dateIso = ref('')
const city = ref('')
const bodyHtml = ref(DEFAULT_CARRIAGE_CONTRACT_BODY)
const customer = ref<CarriagePartyPayload>(emptyCarriageParty())
const carrier = ref<CarriagePartyPayload>(emptyCarriageParty())
const customerDetailsCheck = ref(true)
const carrierDetailsCheck = ref(true)
const loading = ref(false)
const saving = ref(false)

const yellowInputClass =
	'bg-yellow-100 border border-yellow-300 rounded px-1 min-w-[5rem] min-h-[1.5rem] disabled:opacity-80'

/** «на основании Устава» — род. падеж; название документа только если это не тот же Устав. */
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

export function useCarriageContractBlank() {
	const route = useRoute()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const { findDeal } = useDeals()
	const { getCompanyById } = useCompaniesApi()
	const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
	const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
	const slotRevision = useTypedState(Editor.CARRIAGE_CONTRACT_SLOT_REVISION, () => ref(0))

	const dealId = computed(() => Number(route.query.dealId) || 0)
	const currentDeal = computed(() => findDeal(dealId.value))

	const bumpSlot = () => {
		slotRevision.value += 1
	}

	const resolveDocumentId = (): number | null => {
		const fromQuery = Number(route.query.transportDocId)
		if (Number.isFinite(fromQuery) && fromQuery > 0) return fromQuery
		const docs = currentDeal.value?.transportContract?.documents ?? []
		const typed = route.query.transportDocType
			? String(route.query.transportDocType)
			: 'carriage_contract'
		const match =
			docs.find((d) => d.type === typed && d.id) ||
			docs.find((d) => d.type === 'carriage_contract' && d.id) ||
			docs.find((d) => d.id)
		return match?.id ? Number(match.id) : null
	}

	const applyPayload = (payload: CarriageContractPayload | null | undefined) => {
		if (!payload) {
			bodyHtml.value = DEFAULT_CARRIAGE_CONTRACT_BODY
			customer.value = emptyCarriageParty()
			carrier.value = emptyCarriageParty()
			customerDetailsCheck.value = true
			carrierDetailsCheck.value = true
			return
		}
		city.value = payload.city || ''
		bodyHtml.value = payload.bodyHtml || DEFAULT_CARRIAGE_CONTRACT_BODY
		customer.value = { ...emptyCarriageParty(), ...(payload.customer || {}) }
		carrier.value = { ...emptyCarriageParty(), ...(payload.carrier || {}) }
		customerDetailsCheck.value = payload.customerDetailsCheck !== false
		carrierDetailsCheck.value = payload.carrierDetailsCheck !== false
	}

	const loadDocument = async () => {
		const id = resolveDocumentId()
		documentId.value = id
		if (!id) {
			bumpSlot()
			return
		}
		loading.value = true
		try {
			const doc = await purchasesApi.getTransportDocument(id)
			number.value = doc.number || ''
			dateIso.value = doc.date ? String(doc.date).slice(0, 10) : ''
			applyPayload(doc.payload_json as CarriageContractPayload | undefined)
			if (!city.value && currentDeal.value?.seller?.city) {
				city.value = String(currentDeal.value.seller.city)
			}
			bumpSlot()
		} catch (e: any) {
			toast.add({
				title: 'Не удалось загрузить договор перевозки',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const buildPayload = (): CarriageContractPayload => ({
		city: city.value,
		customer: { ...customer.value },
		carrier: { ...carrier.value },
		bodyHtml: bodyHtml.value,
		customerDetailsCheck: customerDetailsCheck.value,
		carrierDetailsCheck: carrierDetailsCheck.value,
	})

	const saveDocument = async (opts?: { silent?: boolean }): Promise<boolean> => {
		if (!documentId.value) {
			toast.add({ title: 'Документ перевозки не выбран', color: 'warning' })
			return false
		}
		saving.value = true
		try {
			const updated = await purchasesApi.updateTransportDocument(documentId.value, {
				number: number.value,
				date: dateIso.value || undefined,
				payload_json: buildPayload() as unknown as Record<string, unknown>,
			})
			number.value = updated.number
			dateIso.value = updated.date ? String(updated.date).slice(0, 10) : dateIso.value
			if (!opts?.silent) {
				toast.add({ title: 'Договор перевозки сохранён', color: 'success' })
			}
			bumpSlot()
			return true
		} catch (e: any) {
			toast.add({
				title: 'Не удалось сохранить',
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
			toast.add({ title: 'Документ перевозки не выбран', color: 'warning' })
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
			if (!bodyHtml.value?.trim()) bodyHtml.value = DEFAULT_CARRIAGE_CONTRACT_BODY
			bumpSlot()
			toast.add({ title: 'Данные из ЛК подставлены', color: 'success' })
		} catch (e: any) {
			toast.add({
				title: 'Не удалось заполнить из ЛК',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const resetBlank = () => {
		bodyHtml.value = DEFAULT_CARRIAGE_CONTRACT_BODY
		customer.value = emptyCarriageParty()
		carrier.value = emptyCarriageParty()
		city.value = ''
		customerDetailsCheck.value = true
		carrierDetailsCheck.value = true
		bumpSlot()
	}

	const applyDefaultBody = () => {
		bodyHtml.value = DEFAULT_CARRIAGE_CONTRACT_BODY
		bumpSlot()
	}

	return {
		documentId,
		number,
		dateIso,
		city,
		bodyHtml,
		customer,
		carrier,
		customerDetailsCheck,
		carrierDetailsCheck,
		loading,
		saving,
		isDisabled,
		dealId,
		currentDeal,
		loadDealTrigger,
		slotRevision,
		yellowInputClass,
		loadDocument,
		saveDocument,
		fillFromLk,
		buildPayload,
		resolveDocumentId,
		resetBlank,
		applyDefaultBody,
		bumpSlot,
	}
}

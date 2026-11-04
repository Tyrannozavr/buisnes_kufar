import { Editor } from '~/constants/keys'
import {
	emptyStrictExpeditionPayload,
	emptyStrictParty,
	isStrictExpeditionType,
	type StrictExpeditionDocType,
	type StrictExpeditionPayload,
	type StrictPartyLine,
} from '~/utils/strictExpeditionDefaults'
import {
	formatGrossNetFromLines,
	formatOrderValue,
	linesWithWeights,
	type WeightLookup,
} from '~/utils/orderCargoTotals'
import { RED_READONLY_CLASS } from '~/utils/carriageParty'
import { usePurchasesApi } from '~/api/purchases'
import { useDeals } from '~/composables/useDeals'
import { useCompaniesApi } from '~/api/companies'
import { useProductsApi } from '~/api/products'
import { useTransportApi } from '~/api/transport'
import type { Company } from '~/types/dealState'

const documentId = ref<number | null>(null)
const number = ref('')
const dateIso = ref('')
const parentId = ref<number | null>(null)
const parentNumber = ref('')
const parentDateIso = ref('')
const payload = ref<StrictExpeditionPayload>(emptyStrictExpeditionPayload())
const loading = ref(false)
const saving = ref(false)
const dialogOpen = ref(false)

/** Почтовый индекс РФ — 6 цифр; отсекаем склейки вроде «1010003323». */
const normalizePostalIndex = (raw: unknown): string => {
	const digits = String(raw ?? '').replace(/\D/g, '')
	if (digits.length >= 6) return digits.slice(0, 6)
	return String(raw ?? '').trim()
}

const officialFromCompany = (
	c: Company | Record<string, any> | null | undefined,
): { name: string; position: string } => {
	const officials = ((c as any)?.officials ?? []) as Array<Record<string, any>>
	const first = officials[0]
	if (!first) return { name: '', position: '' }
	return {
		name: String(first.name || first.full_name || '').trim(),
		position: String(first.position || first.job_title || '').trim(),
	}
}

const partyFromCompany = (c: Company | Record<string, any> | null | undefined, source = ''): StrictPartyLine => {
	if (!c) return emptyStrictParty()
	const fullName =
		String((c as any).fullName || (c as any).full_name || '') ||
		[String((c as any).companyType || (c as any).company_type || ''), String((c as any).companyName || (c as any).company_name || (c as any).name || '')]
			.filter(Boolean)
			.join(' ')
	const official = officialFromCompany(c)
	return {
		fullName: fullName.trim(),
		index: normalizePostalIndex((c as any).index),
		legalAddress: String((c as any).legalAddress || (c as any).legal_address || ''),
		inn: String((c as any).inn ?? ''),
		source,
		officialName: official.name,
		officialPosition: official.position,
	}
}

export function useStrictExpeditionBlank() {
	const route = useRoute()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const transportApi = useTransportApi()
	const productsApi = useProductsApi()
	const { getCompanyById } = useCompaniesApi()
	const { findDeal } = useDeals()
	const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
	const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
	const slotRevision = useTypedState(Editor.STRICT_EXPEDITION_SLOT_REVISION, () => ref(0))

	const dealId = computed(() => Number(route.query.dealId) || 0)
	const currentDeal = computed(() => findDeal(dealId.value))
	const docType = computed((): StrictExpeditionDocType | '' => {
		const t = String(route.query.transportDocType || '')
		return isStrictExpeditionType(t) ? t : ''
	})
	const isStrictTab = computed(() => Boolean(docType.value))

	const bumpSlot = () => {
		slotRevision.value += 1
	}

	const resolveDocumentId = (): number | null => {
		const fromQuery = Number(route.query.transportDocId)
		if (Number.isFinite(fromQuery) && fromQuery > 0) return fromQuery
		const docs = currentDeal.value?.transportContract?.documents ?? []
		const typed = docType.value
		const match =
			(typed && docs.find((d) => d.type === typed && d.id)) ||
			docs.find((d) => d.id)
		return match?.id ? Number(match.id) : null
	}

	const normalizeParty = (raw: Partial<StrictPartyLine> | null | undefined): StrictPartyLine => ({
		...emptyStrictParty(),
		...(raw || {}),
		index: normalizePostalIndex(raw?.index),
	})

	const applyPayload = (raw: StrictExpeditionPayload | null | undefined) => {
		payload.value = {
			...emptyStrictExpeditionPayload(),
			...(raw || {}),
			shipper: normalizeParty(raw?.shipper),
			client: normalizeParty(raw?.client),
			consignee: normalizeParty(raw?.consignee),
			forwarder: normalizeParty(raw?.forwarder),
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
			/* ignore */
		}
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
			applyPayload(doc.payload_json as StrictExpeditionPayload | undefined)
			await loadParent(doc.parent_id)
			bumpSlot()
		} catch (e: any) {
			toast.add({
				title: 'Не удалось загрузить бланк',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const buildPayload = (): StrictExpeditionPayload => ({
		...payload.value,
		shipper: { ...payload.value.shipper },
		client: { ...payload.value.client },
		consignee: { ...payload.value.consignee },
		forwarder: { ...payload.value.forwarder },
	})

	const saveDocument = async (opts?: { silent?: boolean }): Promise<boolean> => {
		if (!documentId.value) {
			toast.add({ title: 'Документ не выбран', color: 'warning' })
			return false
		}
		saving.value = true
		try {
			const updated = await purchasesApi.updateTransportDocument(documentId.value, {
				payload_json: buildPayload() as unknown as Record<string, unknown>,
			})
			number.value = updated.number
			dateIso.value = updated.date ? String(updated.date).slice(0, 10) : dateIso.value
			if (!opts?.silent) toast.add({ title: 'Документ сохранён', color: 'success' })
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

	const listBuyerReceivingAddresses = async (): Promise<string[]> => {
		if (!dealId.value) return []
		try {
			const rows = await purchasesApi.listDealFillAddresses(dealId.value, {
				party: 'buyer',
				kind: 'receiving',
			})
			const sorted = [...(rows || [])].sort(
				(a, b) => Number(Boolean(b.is_default)) - Number(Boolean(a.is_default)),
			)
			return sorted.map((r) => String(r.address || '').trim()).filter(Boolean)
		} catch {
			return []
		}
	}

	const computeWeightsAndValue = async (): Promise<{ weight: string; value: string }> => {
		const deal = currentDeal.value
		const value = formatOrderValue(deal?.product?.amountPrice ?? null)
		const items = deal?.product?.productList ?? []
		const sellerId = deal?.seller?.companyId
		const lookup: WeightLookup = {}
		if (sellerId && items.length) {
			await Promise.all(
				items.slice(0, 20).map(async (item) => {
					const slug = item.slug
					if (!slug) return
					try {
						const p = await productsApi.getProductBySlug(sellerId, slug)
						lookup[slug] = { net: p.net_weight, gross: p.gross_weight }
						if (item.article) lookup[item.article] = lookup[slug]
					} catch {
						/* skip */
					}
				}),
			)
		}
		const weight = formatGrossNetFromLines(linesWithWeights(items, lookup))
		return { weight, value }
	}

	const fillFromLk = async () => {
		if (!documentId.value) {
			toast.add({ title: 'Документ не выбран', color: 'warning' })
			return
		}
		loading.value = true
		try {
			const doc = await purchasesApi.getTransportDocument(documentId.value)
			const deal = currentDeal.value
			const seller = deal?.seller
			const buyer = deal?.buyer

			let forwarderCompany: Record<string, any> | null = null
			try {
				forwarderCompany = (await getCompanyById(
					doc.carrier_company_id,
					false,
				)) as Record<string, any>
			} catch {
				forwarderCompany = null
			}

			let sellerCompany: Record<string, any> | null = null
			const sellerCompanyId = seller?.companyId
			if (sellerCompanyId) {
				try {
					sellerCompany = (await getCompanyById(
						sellerCompanyId,
						false,
					)) as Record<string, any>
				} catch {
					sellerCompany = null
				}
			}

			const next = emptyStrictExpeditionPayload()
			// Реквизиты сторон — из карточек компаний (с officials), fallback на снимок сделки
			next.shipper = partyFromCompany(sellerCompany || seller, 'seller')
			next.client = partyFromCompany(sellerCompany || seller, 'seller')
			next.consignee = partyFromCompany(buyer, 'buyer')
			next.forwarder = partyFromCompany(forwarderCompany, 'forwarder')

			const officials = (forwarderCompany?.officials ?? []) as Array<Record<string, any>>
			const firstFwd = officials[0]
			const sellerOfficial = officialFromCompany(sellerCompany || seller)
			if (docType.value === 'warehouse_receipt' && firstFwd) {
				next.signatureName = String(firstFwd.name || firstFwd.full_name || '')
				next.signaturePosition = String(
					firstFwd.position || firstFwd.job_title || 'Генеральный директор',
				)
			} else {
				// подпись клиента — из ЛК продавца по умолчанию (клиент = поставщик)
				next.signatureName = sellerOfficial.name
				next.signaturePosition =
					sellerOfficial.position || 'Генеральный директор'
			}

			const { weight, value } = await computeWeightsAndValue()
			next.weightGrossNet = weight
			next.value = value

			try {
				const list = await transportApi.listShipments({ deal_id: dealId.value })
				const shipment = list?.[0]
				if (shipment?.id) {
					const cargoRes = await transportApi.getCargo(shipment.id)
					const cargo = cargoRes?.cargo_data || {}
					if (cargo.marking) next.marking = String(cargo.marking)
					if (cargo.volume) next.volume = String(cargo.volume)
					const places = [cargo.places_count, cargo.packaging_type]
						.filter((x) => x != null && x !== '')
						.join(', ')
					if (places) next.placesPackaging = places
				}
			} catch {
				/* optional */
			}

			const destinations = await listBuyerReceivingAddresses()
			if (destinations.length) next.destination = destinations[0]
			else if (buyer?.productionAddress) next.destination = String(buyer.productionAddress)

			if (!next.originCountry) next.originCountry = 'Россия'
			if (!next.transportMode) next.transportMode = 'Автомобильный'

			payload.value = next
			bumpSlot()
			const saved = await saveDocument({ silent: true })
			toast.add({
				title: saved ? 'Данные подставлены и сохранены' : 'Данные подставлены, но не сохранены',
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

	const resetBlank = () => {
		applyPayload(null)
		bumpSlot()
	}

	const setClientFromRole = (role: 'seller' | 'buyer') => {
		const deal = currentDeal.value
		payload.value.client = partyFromCompany(
			role === 'seller' ? deal?.seller : deal?.buyer,
			role,
		)
		bumpSlot()
	}

	const openDialog = () => {
		dialogOpen.value = true
	}

	const applyDialog = async () => {
		dialogOpen.value = false
		bumpSlot()
		await saveDocument()
	}

	return {
		documentId,
		number,
		dateIso,
		parentId,
		parentNumber,
		parentDateIso,
		payload,
		loading,
		saving,
		dialogOpen,
		isDisabled,
		dealId,
		currentDeal,
		docType,
		isStrictTab,
		loadDealTrigger,
		slotRevision,
		redReadonlyClass: RED_READONLY_CLASS,
		loadDocument,
		saveDocument,
		fillFromLk,
		resetBlank,
		setClientFromRole,
		openDialog,
		applyDialog,
		listBuyerReceivingAddresses,
		bumpSlot,
	}
}

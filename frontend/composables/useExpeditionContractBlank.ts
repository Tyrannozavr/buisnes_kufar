import { Editor } from '~/constants/keys'
import {
	DEFAULT_EXPEDITION_CONTRACT_BODY,
	emptyExpeditionContractPayload,
	type ExpeditionContractPayload,
} from '~/utils/expeditionContractDefaults'
import {
	emptyCarriageParty,
	type CarriagePartyPayload,
} from '~/utils/carriageContractDefaults'
import { partyFromCompany, YELLOW_INPUT_CLASS } from '~/utils/carriageParty'
import { usePurchasesApi } from '~/api/purchases'
import { useDeals } from '~/composables/useDeals'
import { getMyCompany } from '~/api/companyOwner'
import { useCompaniesApi } from '~/api/companies'

const documentId = ref<number | null>(null)
const number = ref('')
const dateIso = ref('')
const city = ref('')
const bodyHtml = ref(DEFAULT_EXPEDITION_CONTRACT_BODY)
const client = ref<CarriagePartyPayload>(emptyCarriageParty())
const forwarder = ref<CarriagePartyPayload>(emptyCarriageParty())
const clientDetailsCheck = ref(true)
const forwarderDetailsCheck = ref(true)
const loading = ref(false)
const saving = ref(false)

export function useExpeditionContractBlank() {
	const route = useRoute()
	const toast = useToast()
	const purchasesApi = usePurchasesApi()
	const { findDeal } = useDeals()
	const { getCompanyById } = useCompaniesApi()
	const loadDealTrigger = useTypedState(Editor.LOAD_DEAL_TRIGGER, () => ref(0))
	const isDisabled = useTypedState(Editor.IS_DISABLED, () => ref(true))
	const slotRevision = useTypedState(Editor.EXPEDITION_CONTRACT_SLOT_REVISION, () => ref(0))

	const dealId = computed(() => Number(route.query.dealId) || 0)
	const currentDeal = computed(() => findDeal(dealId.value))
	const isExpeditionDoc = computed(() => {
		const t = String(route.query.transportDocType || '')
		return t === 'expedition_contract' || t === 'transport_expedition'
	})

	const bumpSlot = () => {
		slotRevision.value += 1
	}

	const resolveDocumentId = (): number | null => {
		const fromQuery = Number(route.query.transportDocId)
		if (Number.isFinite(fromQuery) && fromQuery > 0) return fromQuery
		const docs = currentDeal.value?.transportContract?.documents ?? []
		const match =
			docs.find(
				(d) =>
					(d.type === 'expedition_contract' || d.type === 'transport_expedition') &&
					d.id,
			) || docs.find((d) => d.id)
		return match?.id ? Number(match.id) : null
	}

	const applyPayload = (payload: ExpeditionContractPayload | null | undefined) => {
		if (!payload) {
			const empty = emptyExpeditionContractPayload()
			city.value = empty.city
			bodyHtml.value = empty.bodyHtml
			client.value = empty.client
			forwarder.value = empty.forwarder
			clientDetailsCheck.value = true
			forwarderDetailsCheck.value = true
			return
		}
		city.value = payload.city || ''
		bodyHtml.value = payload.bodyHtml || DEFAULT_EXPEDITION_CONTRACT_BODY
		client.value = { ...emptyCarriageParty(), ...(payload.client || {}) }
		forwarder.value = { ...emptyCarriageParty(), ...(payload.forwarder || {}) }
		clientDetailsCheck.value = payload.clientDetailsCheck !== false
		forwarderDetailsCheck.value = payload.forwarderDetailsCheck !== false
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
			applyPayload(doc.payload_json as ExpeditionContractPayload | undefined)
			if (!city.value && currentDeal.value?.seller?.city) {
				city.value = String(currentDeal.value.seller.city)
			}
			bumpSlot()
		} catch (e: any) {
			toast.add({
				title: 'Не удалось загрузить договор экспедиции',
				description: e?.data?.detail || e?.message,
				color: 'error',
			})
		} finally {
			loading.value = false
		}
	}

	const buildPayload = (): ExpeditionContractPayload => ({
		city: city.value,
		client: { ...client.value },
		forwarder: { ...forwarder.value },
		bodyHtml: bodyHtml.value,
		clientDetailsCheck: clientDetailsCheck.value,
		forwarderDetailsCheck: forwarderDetailsCheck.value,
	})

	const saveDocument = async (opts?: { silent?: boolean }): Promise<boolean> => {
		if (!documentId.value) {
			toast.add({ title: 'Договор экспедиции не выбран', color: 'warning' })
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
				toast.add({ title: 'Договор экспедиции сохранён', color: 'success' })
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
			toast.add({ title: 'Договор экспедиции не выбран', color: 'warning' })
			return
		}
		loading.value = true
		try {
			const doc = await purchasesApi.getTransportDocument(documentId.value)
			const owner = await getMyCompany()
			let forwarderCompany: Record<string, any> | null = null
			try {
				forwarderCompany = (await getCompanyById(
					doc.carrier_company_id,
					false,
				)) as Record<string, any>
			} catch {
				forwarderCompany = null
			}
			client.value = partyFromCompany(owner as Record<string, any>)
			forwarder.value = partyFromCompany(forwarderCompany)
			if (!city.value) city.value = client.value.city || city.value
			if (!bodyHtml.value?.trim()) bodyHtml.value = DEFAULT_EXPEDITION_CONTRACT_BODY
			bumpSlot()
			const saved = await saveDocument({ silent: true })
			toast.add({
				title: saved
					? 'Данные из ЛК подставлены и сохранены'
					: 'Данные подставлены, но не сохранены',
				color: saved ? 'success' : 'warning',
			})
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
		const empty = emptyExpeditionContractPayload()
		city.value = empty.city
		bodyHtml.value = empty.bodyHtml
		client.value = empty.client
		forwarder.value = empty.forwarder
		clientDetailsCheck.value = true
		forwarderDetailsCheck.value = true
		bumpSlot()
	}

	const applyDefaultBody = () => {
		bodyHtml.value = DEFAULT_EXPEDITION_CONTRACT_BODY
		bumpSlot()
	}

	return {
		documentId,
		number,
		dateIso,
		city,
		bodyHtml,
		client,
		forwarder,
		clientDetailsCheck,
		forwarderDetailsCheck,
		loading,
		saving,
		isDisabled,
		dealId,
		currentDeal,
		loadDealTrigger,
		slotRevision,
		isExpeditionDoc,
		yellowInputClass: YELLOW_INPUT_CLASS,
		loadDocument,
		saveDocument,
		fillFromLk,
		resetBlank,
		applyDefaultBody,
		bumpSlot,
	}
}

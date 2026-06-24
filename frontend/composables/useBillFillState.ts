const STORAGE_KEY = 'bill-awaiting-fill-deal-ids'

const readDealIds = (): Set<number> => {
	if (!import.meta.client) return new Set()
	try {
		const raw = sessionStorage.getItem(STORAGE_KEY)
		if (!raw) return new Set()
		return new Set(JSON.parse(raw) as number[])
	} catch {
		return new Set()
	}
}

const writeDealIds = (ids: Set<number>) => {
	if (!import.meta.client) return
	sessionStorage.setItem(STORAGE_KEY, JSON.stringify([...ids]))
}

/** После createBill бланк показывает только номер и дату до «Заполнить данными». */
export function useBillFillState() {
	const route = useRoute()
	const revision = useState('billAwaitingFillRevision', () => 0)

	const isAwaitingForDeal = (dealId: number): boolean => {
		revision.value
		return readDealIds().has(dealId)
	}

	const billAwaitingFill = computed(() => {
		const dealId = Number(route.query.dealId)
		return Number.isFinite(dealId) && dealId > 0 && isAwaitingForDeal(dealId)
	})

	const markBillAwaitingFill = (dealId?: number) => {
		const id = dealId ?? Number(route.query.dealId)
		if (!Number.isFinite(id) || id <= 0) return
		const ids = readDealIds()
		ids.add(id)
		writeDealIds(ids)
		revision.value++
	}

	const clearBillAwaitingFill = (dealId?: number) => {
		const id = dealId ?? Number(route.query.dealId)
		if (!Number.isFinite(id) || id <= 0) return
		const ids = readDealIds()
		ids.delete(id)
		writeDealIds(ids)
		revision.value++
	}

	return {
		billAwaitingFill,
		markBillAwaitingFill,
		clearBillAwaitingFill,
		isAwaitingForDeal,
	}
}

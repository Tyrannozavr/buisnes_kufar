import {
	buyerDealsQuery,
	dealsByIdsQuery,
	sellerDealsQuery,
	supplyContractExistsQuery,
	useCreateNewDealVersionQuery,
	useCreateOrderFromCheckoutQuery,
	useCreateSupplyContractEntityQuery,
	useCreateSupplySpecificationQuery,
	useDeleteDealByIdQuery,
	useDeleteLastDealVersionQuery,
	useUpdateDealByIdQuery,
	useCreateBillQuery,
	useCreateContractQuery,
	useCreateSupplyContractQuery
} from "~/queries/purchases"
import { useDealsStore } from "~/stores/deals"
import { QueryKeys } from "~/constants/queryKeys"
import { useQueryCache } from "@pinia/colada"
import {
	createBodyForOrderUpdate,
	createBodyForUpdate,
	responseToDeal,
} from "~/utils/dealsMapper"
import { Editor } from "~/constants/keys"
import { usePurchasesApi } from "~/api/purchases"
import { storeToRefs } from "pinia"
import type { ProductInCheckout } from "~/types/product"
import type { SupplyContractEntityCreate } from "~/types/supplyContractEntity"

type DealsLoadRole = 'buyer' | 'seller' | 'both'
type DealsFetchStatus = 'idle' | 'pending' | 'success' | 'error'

const buyerDealsListStatus = ref<DealsFetchStatus>('idle')
const sellerDealsListStatus = ref<DealsFetchStatus>('idle')
const dealsByIdsStatus = ref<DealsFetchStatus>('idle')
const buyerDealIds = ref<number[]>([])
const sellerDealIds = ref<number[]>([])
const needsBuyerDealsList = ref(false)
const needsSellerDealsList = ref(false)
const dealsLoadPromises = new Map<string, Promise<void>>()

/**
 * Композабл для работы со сделками в store, cache, server(pinia colada).
 * @param options.role — на странице Продажи только seller, Закупки — buyer (быстрее загрузка).
 */
export const useDeals = (options?: { role?: DealsLoadRole }) => {
	const loadRole: DealsLoadRole = options?.role ?? 'both'
	const loadBuyer = loadRole === 'both' || loadRole === 'buyer'
	const loadSeller = loadRole === 'both' || loadRole === 'seller'
	const queryCache = useQueryCache()
	const dealsStore = useDealsStore()
	const { storedIds, deals, lastDeal } = storeToRefs(dealsStore)

	const isBuyerDealsLoading = computed(() => {
		if (!import.meta.client || !needsBuyerDealsList.value) return false
		if (buyerDealsListStatus.value === 'error') return false
		if (buyerDealsListStatus.value !== 'success') return true
		const ids = buyerDealIds.value
		if (!ids.length) return false
		return !ids.every((id) => storedIds.value.includes(id))
	})

	const isSellerDealsLoading = computed(() => {
		if (!import.meta.client || !needsSellerDealsList.value) return false
		if (sellerDealsListStatus.value === 'error') return false
		if (sellerDealsListStatus.value !== 'success') return true
		const ids = sellerDealIds.value
		if (!ids.length) return false
		return !ids.every((id) => storedIds.value.includes(id))
	})
	const {
		findDealByDealNumber,
		findDeal,
		clearStore,
		addNewDeal,
		addNewProduct,
		editSellerCompany,
		editBuyerCompany,
		editProductList,
		editProductComments,
		removeDeal,
		editBillFields,
		editBillDocumentType,
		editBillSupplierDetailsCheck,
		editBillBuyerDetailsCheck,
		editContractDate,
		editContractBinding,
		editSupplyContractDate,
		editAmountWithVatRate,
		editPaymentTerms,
		editAdditionalInfo,
		editOfficialsBill,
		editBillReason,
		editVatRateSeller,
		editAmountVatRate,
		editContractTermsContract,
		editContractTermsTextContract,
		editDeliveryTermsContract,
		editPaymentTermsContract,
		editContractTermsOffer,
		editContractTermsTextOffer,
		editAdditionalInfoOffer,
		editPaymentTermsOffer,
		editAmountExclVat,
		editSupplyContractNumber,
		editSupplyContractSpecificationNumber,
		editSupplyContractSpecificationDate,
		editSupplyContractOfficialsSeller,
		editSupplyContractTemplate,
		editSupplyContractSpecificationTemplate,
		editSupplyContractText,
		editSupplyContractSpecificationText,
		editSupplyContractSupplierDetailsCheck,
		editSupplyContractBuyerDetailsCheck,
		editSupplyContractCoverLetterCheck,
	} = dealsStore

	/** Подтянуть последнюю версию сделки с API и обновить store (для согласования изменений). */
	const refreshDealFromServer = async (dealId: number): Promise<boolean> => {
		try {
			const response = await usePurchasesApi().getDealById(dealId)
			if (!response) return false
			dealsStore.upsertDeal(responseToDeal(response))
			queryCache.setQueryData([QueryKeys.DEAL_BY_ID, dealId], response)
			return true
		} catch (error) {
			console.error("refreshDealFromServer:", error)
			return false
		}
	}

	/** 
	 * Получение сделок с сервера и сохранение в store
	 */
	const getDeals = (): void => {
		if (!import.meta.client) return

		needsBuyerDealsList.value = loadBuyer
		needsSellerDealsList.value = loadSeller

		const roleKey = `${loadBuyer}:${loadSeller}`
		const existing = dealsLoadPromises.get(roleKey)
		if (existing) {
			void existing
			return
		}

		const promise = loadDealsIntoStore().finally(() => {
			dealsLoadPromises.delete(roleKey)
		})
		dealsLoadPromises.set(roleKey, promise)
		void promise
	}

	const loadDealsIntoStore = async (): Promise<void> => {
		const fetchDealIds = async (
			role: 'buyer' | 'seller',
		): Promise<number[]> => {
			const statusRef =
				role === 'buyer' ? buyerDealsListStatus : sellerDealsListStatus
			const idsRef = role === 'buyer' ? buyerDealIds : sellerDealIds
			const queryOpts =
				role === 'buyer' ? buyerDealsQuery({}) : sellerDealsQuery({})
			const entry = queryCache.ensure(queryOpts)

			if (entry.state.value.status === 'success') {
				const ids = (entry.state.value.data ?? []).map((deal) => deal.id)
				idsRef.value = ids
				statusRef.value = 'success'
				return ids
			}

			statusRef.value = 'pending'
			try {
				const { data } = await queryCache.fetch(entry)
				const ids = (data ?? []).map((deal) => deal.id)
				idsRef.value = ids
				statusRef.value = 'success'
				return ids
			} catch (error) {
				console.error(`getDeals ${role} list:`, error)
				statusRef.value = 'error'
				idsRef.value = []
				return []
			}
		}

		const idList: number[] = []

		if (needsBuyerDealsList.value) {
			idList.push(...(await fetchDealIds('buyer')))
		}
		if (needsSellerDealsList.value) {
			for (const id of await fetchDealIds('seller')) {
				if (!idList.includes(id)) idList.push(id)
			}
		}

		if (!idList.length) {
			dealsByIdsStatus.value = 'success'
			return
		}

		const missingIds = idList.filter((id) => !storedIds.value.includes(id))
		if (!missingIds.length) {
			dealsByIdsStatus.value = 'success'
			return
		}

		dealsByIdsStatus.value = 'pending'
		try {
			const entry = queryCache.ensure(dealsByIdsQuery({ ids: idList }))
			if (entry.state.value.status !== 'success') {
				await queryCache.fetch(entry)
			}
			const data = entry.state.value.data

			for (const deal of data ?? []) {
				if (!storedIds.value.includes(deal.id)) {
					dealsStore.addNewDeal(responseToDeal(deal))
				}
			}

			const stillMissing = idList.filter((id) => !storedIds.value.includes(id))
			dealsByIdsStatus.value = stillMissing.length ? 'error' : 'success'
		} catch (error) {
			console.error('getDeals dealsByIds:', error)
			dealsByIdsStatus.value = 'error'
		}
	}

	/**
	 * Удаление сделки по id
	 * @param dealId - id сделки
	 */
	const deleteDeal = (dealId: number): void => {
		removeDeal(dealId)

		const { deleteDealById } = useDeleteDealByIdQuery()
		deleteDealById(dealId)
		queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID, dealId] })
		queryCache.invalidateQueries({ key: [QueryKeys.DEALS_BY_IDS] })
	}

	/**
	 * Создание новой версии сделки(при внесении изменений в сделку)
	 * @param dealId - id сделки
	 * @returns Promise, резолвится после завершения запроса
	 */
	const createNewDealVersion = async (dealId: number): Promise<void> => {
		const route = useRoute()
		const activeTab = useTypedState(Editor.ACTIVE_TAB)
		const orderOnly =
			route.query.role === "buyer" || activeTab.value === "0"
		const body = orderOnly
			? createBodyForOrderUpdate(dealId)
			: createBodyForUpdate(dealId)
		const { createNewDealVersionAsync } = useCreateNewDealVersionQuery()
		await createNewDealVersionAsync(dealId, body)
		queryCache.invalidateQueries({ key: [QueryKeys.DEALS_BY_IDS] })
	}

	/**
	 * Удаление последней версии сделки(при отклонении изменений в сделке)
	 * @param dealId - id сделки
	 */
	const deleteLastDealVersion = (dealId: number): void => {
		const { deleteLastDealVersion } = useDeleteLastDealVersionQuery()
		deleteLastDealVersion(dealId)
		queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID, dealId] })
	}

	/**
	 * Обновление сделки по id
	 * @param dealId - id сделки
	 */
	const updateDeal = (dealId: number): void => {
		const { updateDealById } = useUpdateDealByIdQuery()
		updateDealById(dealId, createBodyForUpdate(dealId) ?? { updated_at: new Date().toISOString() })
		queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID, dealId] })
	}

	/**
	 * Создание счета на основании сделки.
	 * @param fillFromDeal — сразу заполнить бланк (таблица «Продажи», «СЧЕТ на основании» в заказе)
	 */
	const createBill = (
		dealId: number,
		options?: { date?: string; fillFromDeal?: boolean; replace?: boolean },
	): Promise<{ bill_number: string; bill_date: string } | undefined> => {
		const { createBill: createBillMutation } = useCreateBillQuery()
		return createBillMutation(dealId, options)
	}

	/**
	 * Создание договора на основании сделки
	 * @param dealId - id сделки
	 */
	const createContract = (dealId: number): void => {
		const { createContract } = useCreateContractQuery()
		createContract(dealId)
	}

	/**
	 * Legacy: генерирует номер/дату договора поставки на сделке -> договор поставки начинает существовать
	 * @param dealId - id сделки
	 */
	const createSupplyContract = (
		dealId: number,
		date?: string,
	): Promise<{ supply_contract_number: string; supply_contract_date: string } | undefined> => {
		const { createSupplyContract: createSupplyContractMutation } = useCreateSupplyContractQuery()
		return createSupplyContractMutation(dealId, date)
	}

	/**
	 * GET /supply-contracts/exists — есть ли entity-договор на пару компаний
	 */
	const checkSupplyContractExists = async (
		buyerCompanyId: number,
		sellerCompanyId: number,
	) => {
		const opts = supplyContractExistsQuery({ buyerCompanyId, sellerCompanyId })
		const entry = queryCache.ensure(opts)
		const { data } = await queryCache.fetch(entry)
		return data
	}

	/**
	 * POST /supply-contracts — создать entity-договор поставки
	 */
	const createSupplyContractEntity = async (body: SupplyContractEntityCreate) => {
		const { createSupplyContractEntity } = useCreateSupplyContractEntityQuery()
		return createSupplyContractEntity(body)
	}

	/**
	 * POST /supply-contracts/{id}/specifications — создать спецификацию
	 */
	const createSupplySpecification = async (contractId: number) => {
		const { createSupplySpecification } = useCreateSupplySpecificationQuery()
		return createSupplySpecification(contractId)
	}

	/**
	 * POST /checkout — создать заказ из корзины
	 */
	const orderFromCheckout = async (products: ProductInCheckout[]) => {
		const { orderFromCheckout } = useCreateOrderFromCheckoutQuery()
		return orderFromCheckout(products)
	}

	/**
	 * Загрузить одну сделку в store (SSR + клиент). Редактор не рендерит форму до resolve.
	 */
	const ensureDealLoaded = async (dealId: number): Promise<boolean> => {
		if (!dealId || Number.isNaN(dealId)) return false
		if (findDeal(dealId)) return true

		try {
			const response = await usePurchasesApi().getDealById(dealId)
			if (!response) return false
			dealsStore.upsertDeal(responseToDeal(response))
			if (import.meta.client) {
				queryCache.setQueryData([QueryKeys.DEAL_BY_ID, dealId], response)
			}
			return true
		} catch (error) {
			console.error("ensureDealLoaded:", error)
			return false
		}
	}

	return {
		//store functions
		deals,
		lastDeal,
		findDealByDealNumber,
		findDeal,
		clearStore,
		addNewDeal,
		addNewProduct,
		editSellerCompany,
		editBuyerCompany,
		editProductList,
		editProductComments,
		removeDeal,
		editBillFields,
		editBillDocumentType,
		editBillSupplierDetailsCheck,
		editBillBuyerDetailsCheck,
		editContractDate,
		editContractBinding,
		editSupplyContractDate,
		editAmountWithVatRate,
		editPaymentTerms,
		editAdditionalInfo,
		editOfficialsBill,
		editBillReason,
		editVatRateSeller,
		editAmountVatRate,
		editContractTermsContract,
		editContractTermsTextContract,
		editDeliveryTermsContract,
		editPaymentTermsContract,
		editContractTermsOffer,
		editContractTermsTextOffer,
		editAdditionalInfoOffer,
		editPaymentTermsOffer,
		editAmountExclVat,
		editSupplyContractNumber,
		editSupplyContractSpecificationNumber,
		editSupplyContractSpecificationDate,
		editSupplyContractOfficialsSeller,
		editSupplyContractTemplate,
		editSupplyContractSpecificationTemplate,
		editSupplyContractText,
		editSupplyContractSpecificationText,
		editSupplyContractSupplierDetailsCheck,
		editSupplyContractBuyerDetailsCheck,
		editSupplyContractCoverLetterCheck,
		//server functions
		getDeals,
		isBuyerDealsLoading,
		isSellerDealsLoading,
		deleteDeal,
		createNewDealVersion,
		deleteLastDealVersion,
		updateDeal,
		createBill,
		createContract,
		createSupplyContract,
		checkSupplyContractExists,
		createSupplyContractEntity,
		createSupplySpecification,
		orderFromCheckout,
		refreshDealFromServer,
		ensureDealLoaded,
	}
}

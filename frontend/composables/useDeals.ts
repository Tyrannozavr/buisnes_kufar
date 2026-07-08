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
import { createBodyForUpdate, responseToDeal } from "~/utils/dealsMapper"
import { usePurchasesApi } from "~/api/purchases"
import { storeToRefs } from "pinia"
import type { ProductInCheckout } from "~/types/product"
import type { SupplyContractEntityCreate } from "~/types/supplyContractEntity"

type DealsLoadRole = 'buyer' | 'seller' | 'both'

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
		const buyerDealsStatus = ref(loadBuyer ? 'pending' : 'success')
		const sellerDealsStatus = ref(loadSeller ? 'pending' : 'success')
		const buyerDeals = ref<{ id: number }[] | undefined>(loadBuyer ? undefined : [])
		const sellerDeals = ref<{ id: number }[] | undefined>(loadSeller ? undefined : [])

		if (loadBuyer) {
			const buyerQuery = useQuery(() => buyerDealsQuery({}))
			watch(
				() => [buyerQuery.status.value, buyerQuery.data.value] as const,
				([status, data]) => {
					buyerDealsStatus.value = status
					buyerDeals.value = data
				},
				{ immediate: true },
			)
		}

		if (loadSeller) {
			const sellerQuery = useQuery(() => sellerDealsQuery({}))
			watch(
				() => [sellerQuery.status.value, sellerQuery.data.value] as const,
				([status, data]) => {
					sellerDealsStatus.value = status
					sellerDeals.value = data
				},
				{ immediate: true },
			)
		}

		const ids = computed<number[]>(() => {
			const set = new Set<number>()
			if (buyerDealsStatus.value === "success" && buyerDeals.value) {
				buyerDeals.value.forEach((d) => set.add(d.id))
			}
			if (sellerDealsStatus.value === "success" && sellerDeals.value) {
				sellerDeals.value.forEach((d) => set.add(d.id))
			}
			return Array.from(set)
		})

		const isReadyToGetDealsByIds = computed(() => {
			const buyerOk = !loadBuyer || buyerDealsStatus.value === "success"
			const sellerOk = !loadSeller || sellerDealsStatus.value === "success"
			return buyerOk && sellerOk && ids.value.length > 0
		})

		watch(
			[isReadyToGetDealsByIds, ids],
			async ([ready, idList]) => {
				if (!ready || !idList?.length) return

				const opts = dealsByIdsQuery({ ids: idList })
				const entry = queryCache.ensure(opts)
				const { data } = await queryCache.fetch(entry)
				
				data?.forEach((deal) => {
					if (!storedIds.value.includes(deal.id)) {
						dealsStore.addNewDeal(responseToDeal(deal))
					}
				})
			},
			{ immediate: true, deep: true }
		)
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
		const { createNewDealVersionAsync } = useCreateNewDealVersionQuery()
		await createNewDealVersionAsync(dealId, createBodyForUpdate(dealId))
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
		options?: { date?: string; fillFromDeal?: boolean },
	): Promise<{ bill_number: string; bill_date: string } | undefined> => {
		const { createBill: createBillMutation } = useCreateBillQuery()
		return createBillMutation(dealId, options?.date, options?.fillFromDeal)
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
	}
}

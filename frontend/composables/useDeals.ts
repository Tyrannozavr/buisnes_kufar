import {
	buyerDealsQuery,
	dealsByIdsQuery,
	sellerDealsQuery,
	useCreateNewDealVersionQuery,
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
import { storeToRefs } from "pinia"

/**
 * Композабл для работы со сделками в store, cache, server(pinia colada).
 */
export const useDeals = () => {
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
		editSupplyContractsDate,
		editAmountWithVatRate,
		editPaymentTerms,
		editAdditionalInfo,
		editOfficialsBill,
		editBillReason,
		editVatRateSeller,
		editAmountVatRate,
	} = dealsStore

	/** 
	 * Получение сделок с сервера и сохранение в store
	 */
	const getDeals = (): void => {
		const { data: buyerDeals, status: buyerDealsStatus } = useQuery(() =>
			buyerDealsQuery({})
		)
		const { data: sellerDeals, status: sellerDealsStatus } = useQuery(() =>
			sellerDealsQuery({})
		)

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

		const isReadyToGetDealsByIds = computed(
			() =>
				buyerDealsStatus.value === "success" &&
				sellerDealsStatus.value === "success" &&
				ids.value.length > 0
		)

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
	 * Создание счета на основании сделки
	 * @param dealId - id сделки
	 */
	const createBill = (dealId: number): void => {
		const { createBill } = useCreateBillQuery()
		createBill(dealId)
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
	 * Создание договора поставки на основании сделки
	 * @param dealId - id сделки
	 */
	const createSupplyContract = (dealId: number): void => {
		const { createSupplyContract } = useCreateSupplyContractQuery()
		createSupplyContract(dealId)
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
		editSupplyContractsDate,
		editAmountWithVatRate,
		editPaymentTerms,
		editAdditionalInfo,
		editOfficialsBill,
		editBillReason,
		editVatRateSeller,
		editAmountVatRate,
		//server functions
		getDeals,
		deleteDeal,
		createNewDealVersion,
		deleteLastDealVersion,
		updateDeal,
		createBill,
		createContract,
		createSupplyContract
	}
}

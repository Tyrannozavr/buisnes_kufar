import {
	buyerDealsQuery,
	dealsByIdsQuery,
	sellerDealsQuery,
	useCreateNewDealVersionQuery,
	useDeleteDealByIdQuery,
	useDeleteLastDealVersionQuery,
	useUpdateDealByIdQuery
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
	const {
		storedIds,
		deals,
		lastDeal } = storeToRefs(dealsStore)
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
		fullUpdateDeal } = dealsStore

	/**
	 * Получение списка сделок и заполнение ими store
	 */
	const getDeals = (): void => {
		const ids = ref<number[]>([])

		const { data: buyerDeals, status: buyerDealsStatus } = useQuery(() =>buyerDealsQuery({}))
		const { data: sellerDeals, status: sellerDealsStatus } = useQuery(() =>sellerDealsQuery({}))
		const isReadyToGetDealsByIds = computed<boolean>(() => buyerDealsStatus.value === "success" && sellerDealsStatus.value === "success" && ids.value.length > 0)
		const { data: dealsByIds } = useQuery(() => ({
			...dealsByIdsQuery({ids: ids.value}),
			enabled: isReadyToGetDealsByIds.value
			})
		)

		watch(() => buyerDealsStatus.value,
			(status) => {
				if (status === "success") {
					buyerDeals.value?.forEach((deal) => {
						ids.value.push(deal.id)
					})
				}
			},
			{ deep: true, immediate: true, flush: "sync" }
		)

		watch(() => sellerDealsStatus.value,
			(status) => {
				if (status === "success") {
					sellerDeals.value?.forEach((deal) => {
						ids.value.push(deal.id)
					})
				}
			},
			{ deep: true, immediate: true, flush: "sync" }
		)

		watch(() => dealsByIds.value, () => {
			console.log('DEALS BY IDS: ', dealsByIds.value)
			dealsByIds.value?.forEach((deal) => {
				if (!storedIds.value.includes(deal.id)) {
					dealsStore.addNewDeal(responseToDeal(deal))
				}
			})
		}, { deep: true, immediate: false, flush: "sync" })
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
	 */
	const createNewDealVersion = (dealId: number): void => {
		const { createNewDealVersion } = useCreateNewDealVersionQuery()
		createNewDealVersion(dealId, createBodyForUpdate(dealId) ?? {})
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
		updateDealById(dealId, createBodyForUpdate(dealId) ?? {})
		queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID, dealId] })
	}

	return {
		//store refs
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
		fullUpdateDeal,
		//server+store functions
		getDeals,
		deleteDeal,
		createNewDealVersion,
		deleteLastDealVersion,
		updateDeal
	}
}

import { defineMutation, defineQueryOptions, useMutation } from "@pinia/colada";
import { usePurchasesApi } from "~/api/purchases";
import { QueryKeys } from "~/constants/queryKeys";
import type { DealResponse, DealUpdate } from "~/types/dealResponse";
import type { Buyer, ProductInCheckout } from "~/types/product";
import { useQueryCache } from "@pinia/colada";
import { useDeals } from "~/composables/useDeals";

export const buyerDealsQuery = defineQueryOptions(
	({ skip = 0, limit = 100 }: { skip?: number; limit?: number }) => ({
		key: [QueryKeys.BUYER_DEALS, skip, limit],
		query: () => usePurchasesApi().getBuyerDeals(skip, limit),
	})
)

export const sellerDealsQuery = defineQueryOptions(({ skip = 0, limit = 100 }: { skip?: number; limit?: number }) => ({
	key: [QueryKeys.SELLER_DEALS, skip, limit],
	query: () => usePurchasesApi().getSellerDeals(skip, limit),
})
)

export const dealByIdQuery = defineQueryOptions(
	({ dealId }: { dealId: number }) => ({
		key: [QueryKeys.DEAL_BY_ID, dealId],
		query: () => usePurchasesApi().getDealById(dealId)
	})
)

export const dealsByIdsQuery = defineQueryOptions(
	({ ids }: { ids: number[] }) => ({
		key: [QueryKeys.DEALS_BY_IDS, ids],
		query: () => usePurchasesApi().getDealsByIds(ids)
	})
)

export const useUpdateDealByIdQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.UPDATE_DEAL_BY_ID],
		mutation: ({ dealId, body }: { dealId: number, body: DealUpdate }) => usePurchasesApi().updateDealById(dealId, body),
	})
	return {
		...mutation,
		updateDealById: (dealId: number, body: DealUpdate) => mutate({ dealId, body }),
	}
})

export const unitsOfMeasurementQuery = defineQueryOptions(() => ({
	key: [QueryKeys.UNITS_OF_MEASUREMENT],
	query: () => usePurchasesApi().getUnitsOfMeasurement(),
})
)

export const useCreateBillQuery = defineMutation(() => {
	const { editBillFields, findDealByDealNumber, findDeal } = useDeals()
	const queryCache = useQueryCache()
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_BILL],
		mutation: ({ dealId, date }: { dealId: number, date?: string }) => usePurchasesApi().createBill(dealId, date),
		onMutate: ({dealId}) => {
			const deal = findDeal(dealId)
			if (deal) {
				editBillFields(dealId, new Date().toISOString(), deal.sellerOrderNumber)
				queryCache.setQueryData([QueryKeys.DEAL_BY_ID, deal.dealId], deal)
			}
		},
		onSuccess: (data: { bill_number: string, bill_date: string } | undefined) => {
			if (data) {
				const deal = findDealByDealNumber(data.bill_number, 'seller')
				if (deal) {
					editBillFields(deal.dealId, data.bill_date, data.bill_number)
					queryCache.setQueryData([QueryKeys.DEAL_BY_ID, deal.dealId], deal)
				}
			}
		}
	})
	return {
		...mutation,
		createBill: (dealId: number, date?: string) => mutate({ dealId, date }),
	}
})

export const useCreateContractQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_CONTRACT],
		mutation: ({ dealId, date }: { dealId: number, date?: string }) => usePurchasesApi().createContract(dealId, date),
	})
	return {
		...mutation,
		createContract: (dealId: number, date?: string) => mutate({ dealId, date }),
	}
})

export const useCreateSupplyContractQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_SUPPLY_CONTRACT],
		mutation: ({ dealId, date }: { dealId: number, date?: string }) => usePurchasesApi().createSupplyContract(dealId, date),
	})
	return {
		...mutation,
		createSupplyContract: (dealId: number, date?: string) => mutate({ dealId, date }),
	}
})

export const useCreateOrderFromCheckoutQuery = defineMutation(() => {
	const queryCache = useQueryCache()
	const { addNewDeal } = useDeals()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_ORDER_FROM_CHECKOUT],
		mutation: ({
			products,
			buyer,
		}: {
			products: ProductInCheckout[];
			buyer: Buyer;
			}) => usePurchasesApi().createOrderFromCheckout(products, buyer),
		onSuccess: (newDeal: DealResponse) => {
			const deal = responseToDeal(newDeal)
			addNewDeal(deal)
			queryCache.setQueryData([QueryKeys.DEAL_BY_ID, deal.dealId], deal)
		}
	})

	const orderFromCheckout = async (products: ProductInCheckout[], buyer: Buyer) => {
		await mutateAsync({ products, buyer })
	}

	return {
		...mutation,
		orderFromCheckout,
	}
})

export const useDeleteDealByIdQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.DELETE_DEAL_BY_ID],
		mutation: ({ dealId }: { dealId: number }) => usePurchasesApi().deleteDealById(dealId),
	})
	return {
		...mutation,
		deleteDealById: (dealId: number) => mutate({ dealId }),
	}
})

export const useCreateNewDealVersionQuery = defineMutation(() => {
	const { mutate, mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_NEW_DEAL_VERSION],
		mutation: ({ dealId, body }: { dealId: number, body: DealUpdate }) => usePurchasesApi().createNewDealVersion(dealId, body),
	})
	return {
		...mutation,
		createNewDealVersion: (dealId: number, body: DealUpdate) => mutate({ dealId, body }),
		createNewDealVersionAsync: (dealId: number, body: DealUpdate) => mutateAsync({ dealId, body }),
	}
})

export const useDeleteLastDealVersionQuery = defineMutation(() => {
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.DELETE_LAST_DEAL_VERSION],
		mutation: ({ dealId }: { dealId: number }) => usePurchasesApi().deleteLastDealVersion(dealId),
	})
	return {
		...mutation,
		deleteLastDealVersion: (dealId: number) => mutate({ dealId }),
	}
})


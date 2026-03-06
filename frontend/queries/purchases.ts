import { defineMutation, defineQueryOptions, useMutation } from "@pinia/colada";
import { usePurchasesApi } from "~/api/purchases";
import { QueryKeys } from "~/constants/queryKeys";
import type { DealUpdate } from "~/types/dealResponse";
import type { Buyer, ProductInCheckout } from "~/types/product";
import { useQueryCache } from "@pinia/colada";

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
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_BILL],
		mutation: ({ dealId, date }: { dealId: number, date?: string }) => usePurchasesApi().createBill(dealId, date),
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
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_ORDER_FROM_CHECKOUT],
		mutation: ({
			products,
			buyer,
		}: {
			products: ProductInCheckout[];
			buyer: Buyer;
		}) => usePurchasesApi().createOrderFromCheckout(products, buyer),
		onSettled: () => {
			//TODO: существующий кэш сделок покупателя сохранить и перезаписать после пришедшего ответа с сервера
			queryCache.refresh(queryCache.ensure(buyerDealsQuery({})))
			queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID] })
		},
	});

	return {
		...mutation,
		orderFromCheckout: (products: ProductInCheckout[], buyer: Buyer) => mutate({ products, buyer }),
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
	const { mutate, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_NEW_DEAL_VERSION],
		mutation: ({ dealId, body }: { dealId: number, body: DealUpdate }) => usePurchasesApi().createNewDealVersion(dealId, body),
	})
	return {
		...mutation,
		createNewDealVersion: (dealId: number, body: DealUpdate) => mutate({ dealId, body }),
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


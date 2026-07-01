import { defineMutation, defineQueryOptions, useMutation } from "@pinia/colada";
import { usePurchasesApi } from "~/api/purchases";
import { QueryKeys } from "~/constants/queryKeys";
import type { DealResponse, DealUpdate, CheckoutResponse, DealChangeReviewResponse } from "~/types/dealResponse";
import type { ProductInCheckout } from "~/types/product";
import type { SupplyContractEntityCreate } from "~/types/supplyContractEntity";
import type {
	SupplyContractTemplateCreate,
	SupplyContractTemplateType,
	SupplyContractTemplateUpdate,
} from "~/types/supplyContractTemplate";
import { useQueryCache } from "@pinia/colada";
import { useDeals } from "~/composables/useDeals";
import { useBillFillState } from "~/composables/useBillFillState";

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

export const dealChangeReviewQuery = defineQueryOptions(
	({ dealId }: { dealId: number }) => ({
		key: [QueryKeys.DEAL_CHANGE_REVIEW, dealId],
		query: (): Promise<DealChangeReviewResponse> =>
			usePurchasesApi().getDealChangeReview(dealId),
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
	const { markBillAwaitingFill, clearBillAwaitingFill } = useBillFillState()
	const queryCache = useQueryCache()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_BILL],
		mutation: ({
			dealId,
			date,
		}: {
			dealId: number
			date?: string
			fillFromDeal?: boolean
		}) => usePurchasesApi().createBill(dealId, date),
		onMutate: async ({ dealId, fillFromDeal }) => {
			if (!fillFromDeal) {
				markBillAwaitingFill(dealId)
			}
			const deal = findDeal(dealId)
			if (deal) {
				editBillFields(dealId, new Date().toISOString(), deal.sellerOrderNumber)
				await queryCache.setQueryData([QueryKeys.DEAL_BY_ID, deal.dealId], deal)
			}
		},
		onSuccess: async (
			data: { bill_number: string, bill_date: string } | undefined,
			{ dealId, fillFromDeal },
		) => {
			if (data) {
				const deal =
					findDealByDealNumber(data.bill_number, 'seller') ?? findDeal(dealId)
				if (deal) {
					editBillFields(deal.dealId, data.bill_date, data.bill_number)
					if (fillFromDeal) {
						clearBillAwaitingFill(deal.dealId)
					} else {
						markBillAwaitingFill(deal.dealId)
					}
					queryCache.setQueryData([QueryKeys.DEAL_BY_ID, deal.dealId], deal)
				}
			}
		},
	})
	return {
		...mutation,
		createBill: (
			dealId: number,
			date?: string,
			fillFromDeal?: boolean,
		) => mutateAsync({ dealId, date, fillFromDeal }),
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
	const { editSupplyContractDate, editSupplyContractNumber, findDeal } = useDeals()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_SUPPLY_CONTRACT],
		mutation: ({ dealId, date }: { dealId: number, date?: string }) =>
			usePurchasesApi().createSupplyContract(dealId, date),
		onSuccess: async (
			data: { supply_contract_number: string; supply_contract_date: string } | undefined,
			{ dealId },
		) => {
			if (data && findDeal(dealId)) {
				await editSupplyContractDate(dealId, data.supply_contract_date)
				await editSupplyContractNumber(dealId, data.supply_contract_number)
			}
		},
	})
	return {
		...mutation,
		createSupplyContract: (dealId: number, date?: string) => mutateAsync({ dealId, date }),
	}
})

export const supplyContractExistsQuery = defineQueryOptions(
	({
		buyerCompanyId,
		sellerCompanyId,
	}: {
		buyerCompanyId: number
		sellerCompanyId: number
	}) => ({
		key: [QueryKeys.SUPPLY_CONTRACT_EXISTS, buyerCompanyId, sellerCompanyId],
		query: () =>
			usePurchasesApi().checkSupplyContractExists(buyerCompanyId, sellerCompanyId),
	}),
)

export const useCreateSupplyContractEntityQuery = defineMutation(() => {
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_SUPPLY_CONTRACT_ENTITY],
		mutation: (body: SupplyContractEntityCreate) =>
			usePurchasesApi().createSupplyContractEntity(body),
	})
	return {
		...mutation,
		createSupplyContractEntity: (body: SupplyContractEntityCreate) => mutateAsync(body),
	}
})

export const useCreateSupplySpecificationQuery = defineMutation(() => {
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_SUPPLY_SPECIFICATION],
		mutation: ({ contractId }: { contractId: number }) =>
			usePurchasesApi().createSupplySpecification(contractId),
	})
	return {
		...mutation,
		createSupplySpecification: (contractId: number) => mutateAsync({ contractId }),
	}
})

export const useCreateOrderFromCheckoutQuery = defineMutation(() => {
	const queryCache = useQueryCache()
	const { addNewDeal } = useDeals()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_ORDER_FROM_CHECKOUT],
		mutation: ({
			products,
		}: {
			products: ProductInCheckout[];
			}) => usePurchasesApi().createOrderFromCheckout(products),
		onSuccess: (response: CheckoutResponse | undefined) => {
			if (!response?.deals?.length) return
			response.deals.forEach((newDeal: DealResponse) => {
				const deal = responseToDeal(newDeal)
				addNewDeal(deal)
				queryCache.setQueryData([QueryKeys.DEAL_BY_ID, deal.dealId], deal)
			})
			queryCache.invalidateQueries({ key: [QueryKeys.BUYER_DEALS] })
			queryCache.invalidateQueries({ key: [QueryKeys.SELLER_DEALS] })
		}
	})

	const orderFromCheckout = async (products: ProductInCheckout[]) => {
		return mutateAsync({ products })
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

export const useAcceptDealChangesQuery = defineMutation(() => {
	const queryCache = useQueryCache()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.ACCEPT_DEAL_CHANGES],
		mutation: ({ dealId }: { dealId: number }) => usePurchasesApi().acceptDealChanges(dealId),
		onSuccess: (_data, { dealId }) => {
			queryCache.invalidateQueries({ key: [QueryKeys.DEAL_CHANGE_REVIEW, dealId] })
			queryCache.invalidateQueries({ key: [QueryKeys.DEALS_BY_IDS] })
			queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID, dealId] })
		},
	})
	return {
		...mutation,
		acceptDealChangesAsync: (dealId: number) => mutateAsync({ dealId }),
	}
})

export const useRejectDealChangesQuery = defineMutation(() => {
	const queryCache = useQueryCache()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.REJECT_DEAL_CHANGES],
		mutation: ({ dealId }: { dealId: number }) => usePurchasesApi().rejectDealChanges(dealId),
		onSuccess: (_data, { dealId }) => {
			queryCache.invalidateQueries({ key: [QueryKeys.DEAL_CHANGE_REVIEW, dealId] })
			queryCache.invalidateQueries({ key: [QueryKeys.DEALS_BY_IDS] })
			queryCache.invalidateQueries({ key: [QueryKeys.DEAL_BY_ID, dealId] })
		},
	})
	return {
		...mutation,
		rejectDealChangesAsync: (dealId: number) => mutateAsync({ dealId }),
	}
})

export const supplyContractTemplatesQuery = defineQueryOptions(
	({ type }: { type: SupplyContractTemplateType }) => ({
		key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATES, type],
		query: () => usePurchasesApi().getSupplyContractTemplates(type),
	}),
)

export const supplyContractTemplateDefaultQuery = defineQueryOptions(
	({ type }: { type: SupplyContractTemplateType }) => ({
		key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATE_DEFAULT, type],
		query: () => usePurchasesApi().getDefaultSupplyContractTemplate(type),
	}),
)

export const useCreateSupplyContractTemplateQuery = defineMutation(() => {
	const queryCache = useQueryCache()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.CREATE_SUPPLY_CONTRACT_TEMPLATE],
		mutation: (body: SupplyContractTemplateCreate) =>
			usePurchasesApi().createSupplyContractTemplate(body),
		onSuccess: (_data, body) => {
			queryCache.invalidateQueries({ key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATES, body.type] })
			queryCache.invalidateQueries({ key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATE_DEFAULT, body.type] })
		},
	})
	return {
		...mutation,
		createSupplyContractTemplate: (body: SupplyContractTemplateCreate) => mutateAsync(body),
	}
})

export const useUpdateSupplyContractTemplateQuery = defineMutation(() => {
	const queryCache = useQueryCache()
	const { mutateAsync, ...mutation } = useMutation({
		key: [QueryKeys.UPDATE_SUPPLY_CONTRACT_TEMPLATE],
		mutation: ({
			templateId,
			body,
			type,
		}: {
			templateId: number
			body: SupplyContractTemplateUpdate
			type: SupplyContractTemplateType
		}) => usePurchasesApi().updateSupplyContractTemplate(templateId, body),
		onSuccess: (_data, variables) => {
			queryCache.invalidateQueries({ key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATES, variables.type] })
			queryCache.invalidateQueries({ key: [QueryKeys.SUPPLY_CONTRACT_TEMPLATE_DEFAULT, variables.type] })
		},
	})
	return {
		...mutation,
		updateSupplyContractTemplate: (
			templateId: number,
			body: SupplyContractTemplateUpdate,
			type: SupplyContractTemplateType,
		) => mutateAsync({ templateId, body, type }),
	}
})


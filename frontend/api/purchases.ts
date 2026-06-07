import { API_URLS } from "~/constants/urls"
import type { Buyer, ProductInCheckout } from "~/types/product"
import type { DealResponse, DealUpdate, BuyerDealResponse, SellerDealResponse } from "~/types/dealResponse"
import type {
	SupplyContractEntityCreate,
	SupplyContractEntityResponse,
	SupplyContractEntityUpdate,
	SupplyContractExistsResponse,
	SpecificationEntityResponse,
	SpecificationEntityUpdate,
} from "~/types/supplyContractEntity"
import type {
	SupplyContractTemplate,
	SupplyContractTemplateCreate,
	SupplyContractTemplateUpdate,
} from "~/types/supplyContractTemplate"
import { normalizeApiPath } from "~/utils/normalize";

export const usePurchasesApi = () => {
	const { $api } = useNuxtApp()

	const createDeal = async (
		products: ProductInCheckout[],
		buyer: Buyer
	): Promise<any> => {
		if (products[0]) {
			const bodyPost = {
				items: products.map((el) => ({
					product_article: el.article,
					quantity: el.quantity
				})),
				comments: ""
			}

			try {
				const response = await $api.post(
					normalizeApiPath(API_URLS.CREATE_DEAL),
					bodyPost
				)
				return response
			} catch (err: any) {
				console.log("POST ERROR: ", err)
			}
		}
	}

	const getBuyerDeals = async (
		skip: number = 0,
		limit: number = 100
	): Promise<BuyerDealResponse[] | undefined> => {
		try {
			const response = await $api.get(normalizeApiPath(API_URLS.GET_BUYER_DEALS), {
				query: { skip, limit }
			})
			return response
		} catch (e) {
			console.log("ERROR: ", e)
		}
	}

	const getSellerDeals = async (
		skip: number = 0,
		limit: number = 100
	): Promise<SellerDealResponse[] | undefined> => {
		try {
			const response = await $api.get(
				normalizeApiPath(API_URLS.GET_SELLER_DEALS),
				{
					query: { skip, limit }
				}
			)
			return response
		} catch (e) {
			console.log("ERROR: ", e)
		}
	}

	const getDealById = async (
		deal_id: number
	): Promise<DealResponse | undefined> => {
		try {
			const response = await $api.get(
				normalizeApiPath(API_URLS.GET_DEAL_BY_ID(deal_id))
			)
			return response
		} catch (error) {
			console.log("ERROR GET DEAL BY ID: ", error)
		}
	}

	const getDealsByIds = async (
		ids: number[]
	): Promise<DealResponse[] | undefined> => {
		try {
			const response = await $api.post(
				normalizeApiPath(API_URLS.GET_DEALS_BY_IDS),
				{ ids }
			)
			return response
		} catch (error) {
			console.log("ERROR GET DEALS BY IDS: ", error)
		}
	}

	const updateDealById = async (
		deal_id: number,
		body: DealUpdate | Record<string, unknown> = {}
	) => {
		try {
			const response = await $api.put(
				normalizeApiPath(API_URLS.PUT_DEAL_BY_ID(deal_id)),
				body
			)
			return response
		} catch (error) {
			console.log("ERROR: ", error)
			throw error
		}
	}

	const createOrderFromCheckout = async (
		products: ProductInCheckout[],
		buyer: Buyer
	) => {
		if (!products?.length) return

		const bodyPost = {
			items: products.map((product) => ({
				slug: String(product.slug),
				description: product.description ?? null,
				logoUrl: product.logoUrl ?? null,
				productName: String(product.productName),
				article:
					product.article != null && String(product.article).trim() !== ''
						? String(product.article).trim()
						: '',
				quantity: Number.isFinite(product.quantity) ? product.quantity : 1,
				units: product.units ? String(product.units) : "шт",
				price: Number.isFinite(product.price) ? product.price : 0,
				amount: Number.isFinite(product.amount) ? product.amount : 0,
				companyId: buyer.companyId,
				companyName: String(buyer.companyName),
				companySlug: String(buyer.companySlug)
			})),
			comments: ""
		}

		try {
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_ORDER_FROM_CHECKOUT),
				bodyPost
			)
			return response
		} catch (err: any) {
			console.log("POST ERROR: ", err)
			throw err
		}
	}

	const getUnitsOfMeasurement = async () => {
		try {
			const response = await $api.get(
				normalizeApiPath(API_URLS.GET_UNITS_MEASUREMENT)
			)
			return response
		} catch (error) {
			console.log("ERROR: ", error)
		}
	}

	const createBill = async (dealId: number, date?: string):Promise<{bill_number: string, bill_date: string} | undefined> => {
		try {
			const body = date ? { date } : {}
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_BILL(dealId)),
				body
			)
			return response
		} catch (error) {
			console.log("ERROR: ", error)
		}
	}

	const createContract = async (dealId: number, date?: string):Promise<{contract_number: string, contract_date: string} | undefined> => {
		try {
			const body = date ? { date } : {}
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_CONTRACT(dealId)),
				body
			)
			return response
		} catch (error) {
			console.log("ERROR: ", error)
		}
	}

	const createSupplyContract = async (dealId: number, date?: string):Promise<{supply_contract_number: string, supply_contract_date: string} | undefined> => {
		try {
			const body = date ? { date } : {}
			const response = await $api.post(
				normalizeApiPath(API_URLS.ASSIGN_DEAL_SUPPLY_CONTRACT_NUMBER(dealId)),
				body
			)
			return response
		} catch (error) {
			console.log("ERROR: ", error)
		}
	}

	const checkSupplyContractExists = async (
		buyerCompanyId: number,
		sellerCompanyId: number,
	): Promise<SupplyContractExistsResponse | undefined> => {
		try {
			return await $api.get(normalizeApiPath(API_URLS.GET_SUPPLY_CONTRACT_EXISTS), {
				query: {
					buyer_company_id: buyerCompanyId,
					seller_company_id: sellerCompanyId,
				},
			})
		} catch (error) {
			console.log("ERROR checkSupplyContractExists: ", error)
			throw error
		}
	}

	const createSupplyContractEntity = async (
		body: SupplyContractEntityCreate,
	): Promise<SupplyContractEntityResponse | undefined> => {
		try {
			return await $api.post(normalizeApiPath(API_URLS.CREATE_SUPPLY_CONTRACT_ENTITY), body)
		} catch (error) {
			console.log("ERROR createSupplyContractEntity: ", error)
			throw error
		}
	}

	const updateSupplyContractEntity = async (
		contractId: number,
		body: SupplyContractEntityUpdate,
	): Promise<SupplyContractEntityResponse | undefined> => {
		try {
			return await $api.patch(
				normalizeApiPath(API_URLS.UPDATE_SUPPLY_CONTRACT_ENTITY(contractId)),
				body,
			)
		} catch (error) {
			console.log("ERROR updateSupplyContractEntity: ", error)
			throw error
		}
	}

	const getSupplyContractEntity = async (
		contractId: number,
	): Promise<SupplyContractEntityResponse | undefined> => {
		try {
			return await $api.get(normalizeApiPath(API_URLS.GET_SUPPLY_CONTRACT_ENTITY(contractId)))
		} catch (error) {
			console.log("ERROR getSupplyContractEntity: ", error)
			throw error
		}
	}

	const createSupplySpecification = async (
		contractId: number,
	): Promise<SpecificationEntityResponse | undefined> => {
		try {
			return await $api.post(
				normalizeApiPath(API_URLS.CREATE_SUPPLY_CONTRACT_SPECIFICATION(contractId)),
				{},
			)
		} catch (error) {
			console.log("ERROR createSupplySpecification: ", error)
			throw error
		}
	}

	const updateSupplySpecification = async (
		specId: number,
		body: SpecificationEntityUpdate,
	): Promise<SpecificationEntityResponse | undefined> => {
		try {
			return await $api.patch(
				normalizeApiPath(API_URLS.UPDATE_SUPPLY_CONTRACT_SPECIFICATION(specId)),
				body,
			)
		} catch (error) {
			console.log("ERROR updateSupplySpecification: ", error)
			throw error
		}
	}

	const bindSupplyContractToDeal = async (
		dealId: number,
		contractId: number,
	): Promise<{ bound: boolean } | undefined> => {
		try {
			return await $api.post(
				normalizeApiPath(API_URLS.BIND_DEAL_SUPPLY_CONTRACT_ENTITY(dealId)),
				{ contract_id: contractId },
			)
		} catch (error) {
			console.log("ERROR bindSupplyContractToDeal: ", error)
			throw error
		}
	}

	const bindSupplySpecificationToDeal = async (
		dealId: number,
		specId: number,
	): Promise<{ bound: boolean } | undefined> => {
		try {
			return await $api.post(
				normalizeApiPath(API_URLS.BIND_DEAL_SUPPLY_SPECIFICATION(dealId)),
				{ spec_id: specId },
			)
		} catch (error) {
			console.log("ERROR bindSupplySpecificationToDeal: ", error)
			throw error
		}
	}

	const getSupplyContractTemplates = async (
		type: 'supply_contract' | 'specification',
	): Promise<SupplyContractTemplate[] | undefined> => {
		try {
			return await $api.get(normalizeApiPath(API_URLS.GET_SUPPLY_CONTRACT_TEMPLATES), {
				query: { type },
			})
		} catch (error) {
			console.log("ERROR getSupplyContractTemplates: ", error)
			throw error
		}
	}

	const getDefaultSupplyContractTemplate = async (
		type: 'supply_contract' | 'specification',
	): Promise<SupplyContractTemplate | undefined> => {
		try {
			return await $api.get(normalizeApiPath(API_URLS.GET_SUPPLY_CONTRACT_TEMPLATE_DEFAULT), {
				query: { type },
			})
		} catch (error) {
			console.log("ERROR getDefaultSupplyContractTemplate: ", error)
			return undefined
		}
	}

	const createSupplyContractTemplate = async (
		body: SupplyContractTemplateCreate,
	): Promise<SupplyContractTemplate | undefined> => {
		try {
			return await $api.post(normalizeApiPath(API_URLS.GET_SUPPLY_CONTRACT_TEMPLATES), body)
		} catch (error) {
			console.log("ERROR createSupplyContractTemplate: ", error)
			throw error
		}
	}

	const updateSupplyContractTemplate = async (
		templateId: number,
		body: SupplyContractTemplateUpdate,
	): Promise<SupplyContractTemplate | undefined> => {
		try {
			return await $api.patch(
				normalizeApiPath(API_URLS.SUPPLY_CONTRACT_TEMPLATE(templateId)),
				body,
			)
		} catch (error) {
			console.log("ERROR updateSupplyContractTemplate: ", error)
			throw error
		}
	}

	const deleteSupplyContractTemplate = async (templateId: number) => {
		try {
			return await $api.delete(normalizeApiPath(API_URLS.SUPPLY_CONTRACT_TEMPLATE(templateId)))
		} catch (error) {
			console.log("ERROR deleteSupplyContractTemplate: ", error)
			throw error
		}
	}

	const deleteDealById = async (deal_id: number) => {
		try {
			const response = await $api.delete(
				normalizeApiPath(API_URLS.DELETE_DEAL_BY_ID(deal_id))
			)
			return response
		} catch (error) {
			console.log("ERROR: ", error)
		}
	}

	const createNewDealVersion = async (
		deal_id: number,
		body: DealUpdate
	): Promise<DealResponse | undefined> => {
		try {
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_NEW_DEAL_VERSION(deal_id)),
				body
			)
			return response
		} catch (e) {
			console.log("ERROR: ", e)
			throw e
		}
	}

	const deleteLastDealVersion = async (deal_id: number) => {
		try {
			const response = await $api.delete(
				normalizeApiPath(API_URLS.DELETE_LAST_DEAL_VERSION(deal_id))
			)
		} catch (e) {
			console.log("ERROR: ", e)
		}
	}

	return {
		createDeal,
		getBuyerDeals,
		getSellerDeals,
		getDealById,
		getDealsByIds,
		updateDealById,
		createBill,
		createContract,
		createSupplyContract,
		checkSupplyContractExists,
		createSupplyContractEntity,
		updateSupplyContractEntity,
		getSupplyContractEntity,
		createSupplySpecification,
		updateSupplySpecification,
		bindSupplyContractToDeal,
		bindSupplySpecificationToDeal,
		getSupplyContractTemplates,
		getDefaultSupplyContractTemplate,
		createSupplyContractTemplate,
		updateSupplyContractTemplate,
		deleteSupplyContractTemplate,
		createOrderFromCheckout,
		getUnitsOfMeasurement,
		deleteDealById,
		createNewDealVersion,
		deleteLastDealVersion
	}
}
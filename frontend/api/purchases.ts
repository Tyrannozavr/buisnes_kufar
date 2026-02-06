import { API_URLS } from "~/constants/urls"
import type { Buyer, ProductInCheckout } from "~/types/product"
import type { DealResponse } from "~/types/dealState"

export const usePurchasesApi = () => {
	const { $api } = useNuxtApp()

	// API_URLS.* historically contains "/api/..." paths, but $api already has baseURL="/api"
	// so we normalize to avoid "/api/api/..."
	const normalizeApiPath = (url: string) => (url.startsWith('/api/') ? url.replace(/^\/api/, '') : url)

	const createDeal = async (products: ProductInCheckout[], buyer: Buyer): Promise<any> => {
		if (products[0]) {
			const bodyPost = {
				items: products.map(el => ({
					product_article: el.article,
					quantity: el.quantity,
				})), 
				comments: '',
			}

			try {
				const response = await $api.post(normalizeApiPath(API_URLS.CREATE_DEAL), bodyPost)
				console.log(response)
				return response
			} catch (err: any) {
				console.log('POST ERROR: ', err)
			}
		}
	}
	
	const getBuyerDeals = async (skip: number = 0, limit: number = 100) => {
		try {
			const response = await $api.get(normalizeApiPath(API_URLS.GET_BUYER_DEALS), {
				query: { skip, limit },
			})
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}
	
	const getSellerDeals = async (skip: number = 0, limit: number = 100) => {
		try {
			const response = await $api.get(normalizeApiPath(API_URLS.GET_SELLER_DEALS), {
				query: { skip, limit },
			})
			console.log('RESPONSE: ',response)
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}

	const getDealById = async (deal_id: number): Promise<DealResponse | undefined> => {
		try {
      const response = await $api.get(normalizeApiPath(API_URLS.GET_DEAL_BY_ID(deal_id)))
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}
	
	const putDealById = async (deal_id: number) => {
		try {
			const response = await $api.put(normalizeApiPath(API_URLS.PUT_DEAL_BY_ID(deal_id)), {})
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const uploadDocumentById = async (deal_id: number, formData?: FormData) => {
		try {
			const response = await $api.post(
				normalizeApiPath(API_URLS.UPLOAD_DOCUMENT_BY_ID(deal_id)),
				formData ?? {},
			)
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const createOrderFromCheckout = async (products: ProductInCheckout[], buyer: Buyer) => {
		// NOTE: backend CheckoutRequest expects shape: { items: CheckoutItem[], comments?: string }
		// where companyId/companyName/companySlug belong to SELLER company for each item.
		if (!products?.length) return

		const bodyPost = {
			items: products.map((product) => ({
				slug: String(product.slug),
				// Optional fields in Pydantic are still required if no default is set.
				// Also `undefined` gets dropped by JSON.stringify -> causes 422 "field required".
				description: product.description ?? null,
				logoUrl: product.logoUrl ?? null,
				type: String(product.type),
				position: Number.isFinite(product.position) ? product.position : 1,
				productName: String(product.productName),
				// Backend currently validates `article` as int; fall back to 0 to keep payload valid.
				article: Number.isFinite(product.article) ? product.article : 0,
				quantity: Number.isFinite(product.quantity) ? product.quantity : 1,
				units: product.units ? String(product.units) : 'шт',
				price: Number.isFinite(product.price) ? product.price : 0,
				amount: Number.isFinite(product.amount) ? product.amount : 0,
				companyId: buyer.companyId,
				companyName: String(buyer.companyName),
				companySlug: String(buyer.companySlug),
			})),
			comments: '',
		}

		try {
			const response = await $api.post(normalizeApiPath(API_URLS.CREATE_ORDER_FROM_CHECKOUT), bodyPost)
			console.log(response)
			return response
		} catch (err: any) {
			console.log('POST ERROR: ', err)
		}
	}

	const getUnitsOfMeasurement = async () => {
		try {
			const response = await $api.get(normalizeApiPath(API_URLS.GET_UNITS_MEASUREMENT))
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	return {
		createDeal,
		getBuyerDeals,
		getSellerDeals,
		getDealById,
		putDealById,
		uploadDocumentById,
		createOrderFromCheckout,
		getUnitsOfMeasurement,
	}
}
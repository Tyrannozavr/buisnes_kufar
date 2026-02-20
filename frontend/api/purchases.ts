import { API_URLS } from "~/constants/urls"
import type { Buyer, ProductInCheckout } from "~/types/product"
import type { DealResponse, DealUpdate, BuyerDealResponse, SellerDealResponse } from "~/types/dealReasponse"
import { normalizeApiPath } from "~/utils/normalize";

export const usePurchasesApi = () => {
	const { $api } = useNuxtApp()

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
	
	const getBuyerDeals = async (skip: number = 0, limit: number = 100): Promise<BuyerDealResponse[] | undefined> => {
		try {
			const response = await $api.get(normalizeApiPath(API_URLS.GET_BUYER_DEALS), {
				query: { skip, limit },
      })
      // console.log('RESPONSE GET BUYER DEALS: ', response)
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}
	
	const getSellerDeals = async (skip: number = 0, limit: number = 100): Promise<SellerDealResponse[] | undefined> => {
		try {
			const response = await $api.get(normalizeApiPath(API_URLS.GET_SELLER_DEALS), {
				query: { skip, limit },
      })
      // console.log('RESPONSE GET SELLER DEALS: ', response)
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}

	const getDealById = async (deal_id: number): Promise<DealResponse | undefined> => {
		try {
      const response = await $api.get(normalizeApiPath(API_URLS.GET_DEAL_BY_ID(deal_id)))
      console.log('RESPONSE GET DEAL BY ID: ', response)
			return response
		} catch (error) {
			console.log('ERROR GET DEAL BY ID: ', error)
		}
	}
	
	const updateDealById = async (deal_id: number, body: DealUpdate | Record<string, unknown> = {}) => {
		try {
			const response = await $api.put(normalizeApiPath(API_URLS.PUT_DEAL_BY_ID(deal_id)), body)
			return response
		} catch (error) {
			console.log('ERROR: ', error)
			throw error
		}
	}



	const createOrderFromCheckout = async (products: ProductInCheckout[], buyer: Buyer) => {
		if (!products?.length) return

		const bodyPost = {
			items: products.map((product) => ({
				slug: String(product.slug),
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
      const response = await $api.get(
        normalizeApiPath(API_URLS.GET_UNITS_MEASUREMENT),
      );
      return response;
    } catch (error) {
      console.log("ERROR: ", error);
    }
  }
  
	const createBill = async (dealId: number, date?: string) => {
		try {
			const body = date ? { date } : {}
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_BILL(dealId)),
				body
      )
      console.log("RESPONSE: ", response);
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const createContract = async (dealId: number, date?: string) => {
		try {
			const body = date ? { date } : {}
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_CONTRACT(dealId)),
				body
			)
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const createSupplyContract = async (dealId: number, date?: string) => {
		try {
			const body = date ? { date } : {}
			const response = await $api.post(
				normalizeApiPath(API_URLS.CREATE_SUPPLY_CONTRACT(dealId)),
				body
			)
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const deleteDealById = async (deal_id: number) => {
    try {
      const response = await $api.delete(
        normalizeApiPath(API_URLS.DELETE_DEAL_BY_ID(deal_id)),
      );
      console.log("RESPONSE: ", response);
      return response;
    } catch (error) {
      console.log("ERROR: ", error);
    }
  };

  const createNewDealVersion = async (deal_id: number, body: DealUpdate): Promise<DealResponse | undefined> => {
    try {
      const response = await $api.post(
        normalizeApiPath(API_URLS.CREATE_NEW_DEAL_VERSION(deal_id)),
        body
      );
      return response;
    } catch (e) {
      console.log("ERROR: ", e);
    }
  }

  const deleteLastDealVersion = async (deal_id: number) => {
    try {
      const response = await $api.delete(
        normalizeApiPath(API_URLS.DELETE_LAST_DEAL_VERSION(deal_id))
      )
      console.log("RESPONSE delete last version", response )
    } catch(e) {
      console.log("ERROR: ", e)
    }
  }

	return {
    createDeal,
    getBuyerDeals,
    getSellerDeals,
    getDealById,
    updateDealById,
    createBill,
    createContract,
    createSupplyContract,
    createOrderFromCheckout,
    getUnitsOfMeasurement,
    deleteDealById,
    createNewDealVersion,
    deleteLastDealVersion,
  };
}
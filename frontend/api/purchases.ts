import { API_URLS } from "~/constants/urls"
import type { Buyer, ProductInCheckout } from "~/types/product"
import type { DealResponse, DealUpdate, BuyerDealResponse, SellerDealResponse, DealVersionItem } from "~/types/dealResponse"
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
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}

	const getDealById = async (deal_id: number, version?: number): Promise<DealResponse | undefined> => {
		try {
			const url = version != null
				? `${normalizeApiPath(API_URLS.GET_DEAL_BY_ID(deal_id))}?version=${version}`
				: normalizeApiPath(API_URLS.GET_DEAL_BY_ID(deal_id))
			const response = await $api.get(url)
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
				productName: String(product.productName),
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
    } catch(e) {
      console.log("ERROR: ", e)
    }
  }

  const getDealVersions = async (deal_id: number): Promise<DealVersionItem[] | undefined> => {
    try {
      const response = await $api.get(normalizeApiPath(API_URLS.GET_DEAL_VERSIONS(deal_id)))
      return response
    } catch (e) {
      console.log("ERROR getDealVersions: ", e)
    }
  }

  const acceptDealVersion = async (deal_id: number, version: number): Promise<DealResponse | undefined> => {
    try {
      const response = await $api.post(normalizeApiPath(API_URLS.ACCEPT_DEAL_VERSION(deal_id, version)))
      return response
    } catch (e) {
      console.log("ERROR acceptDealVersion: ", e)
    }
  }

  const rejectDealVersion = async (deal_id: number, version: number): Promise<DealResponse | undefined> => {
    try {
      const response = await $api.post(normalizeApiPath(API_URLS.REJECT_DEAL_VERSION(deal_id, version)))
      return response
    } catch (e) {
      console.log("ERROR rejectDealVersion: ", e)
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
    getDealVersions,
    acceptDealVersion,
    rejectDealVersion,
  };
}
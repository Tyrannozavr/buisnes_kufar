import { API_URLS } from "~/constants/urls"
import type { Buyer, ProductInCheckout } from "~/types/product"

export const usePurchasesApi = () => {

	const postPurchases = async (products: ProductInCheckout[], buyer: Buyer) => {
		if (products[0]) {
			const bodyPost = {
				seller_company_id: buyer.companyId,
				deal_type: products?.[0].type,
				items: products.map(el => ({
					product_name: el.productName,
					product_slug: el.slug,
					product_description: el.description,
					product_article: el.article,
					product_type: el.type,
					logo_url: el.logoUrl,
					quantity: el.quantity,
					unit_of_measurement: el.units,
					price: el.price,
					position: el.position,// это свойстов чисто для компонента checkout
					product_id: `${el.price}${el.article}`//?????? нет такого свойства у продукта 
				})), 
				comments: '',
			}

			try {
				const response = await $fetch(API_URLS.CREATE_DEAL, {
					method: 'POST', 
					body: bodyPost,
				})
				console.log(response)
			} catch (err: any) {
				console.log('POST ERROR: ', err)
			}
		}
	}
	
	const getBuyerDeals = async (skip: number = 0, limit: number = 100) => {
		try {
			const response = await $fetch(API_URLS.GET_BUYER_DEALS, {
				method: 'GET',
				query: {
					skip: skip,
					limit: limit,
				}
			})
			console.log('RESPONSE: ',response)
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}
	
	const getSellerDeals = async (skip: number = 0, limit: number = 100) => {
		try {
			const response = await $fetch(API_URLS.GET_SELLER_DEALS, {
				method: 'GET',
				query: {
					skip: skip,
					limit: limit,
				}
			})
			console.log('RESPONSE: ',response)
			return response
		} catch(e) {
			console.log('ERROR: ', e)
		}
	}

	const getDealById = async (deal_id: number) => {
		try {
			const response = await $fetch(API_URLS.GET_DEAL_BY_ID(deal_id))
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}
	
	const putDealById = async (deal_id: number) => {
		try {
			const response = await $fetch(API_URLS.GET_DEAL_BY_ID(deal_id))
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const uploadDocumentById = async (deal_id: number) => {
		try {
			const response = await $fetch(API_URLS.UPLOAD_DOCUMENT_BY_ID(deal_id),{method: 'POST'})
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	const createOrderFromCheckout = async (products: ProductInCheckout[], buyer: Buyer) => {
		if (products[0]) {
			const bodyPost = products.map(el => ({
				items: products.map(el => ({
					slug: el.slug,
					description: el.description,
					logoUrl: el.logoUrl,
					type: el.type,
					position: el.position,// это свойстов чисто для компонента checkout
					productName: el.productName,
					article: el.article,
					quantity: el.quantity,
					units: el.units,
					price: el.price,
					amount: el.amount,
					companyId: buyer.companyId,
					companyName: buyer.companyName,
					companySlug: buyer.companySlug,
				})), 
				comments: '',
			}))

			try {
				const response = await $fetch(API_URLS.CREATE_ORDER_FROM_CHECKOUT, {
					method: 'POST', 
					body: bodyPost,
				})
				console.log(response)
			} catch (err: any) {
				console.log('POST ERROR: ', err)
			}
		}
	}

	const getUnitsOfMeasurement = async () => {
		try {
			const response = await $fetch(API_URLS.GET_UNITS_MEASUREMENT)
			return response
		} catch (error) {
			console.log('ERROR: ', error)
		}
	}

	return {
		postPurchases,
		getBuyerDeals,
		getSellerDeals,
		getDealById,
		putDealById,
		uploadDocumentById,
		createOrderFromCheckout,
		getUnitsOfMeasurement,
	}
}
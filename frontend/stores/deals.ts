import { defineStore } from "pinia"
import type { Deal, EditPersonCompany, ProductItem } from "~/types/dealState"
import numberToWordsRuPkg from "number-to-words-ru"

const numberToWordsRu = numberToWordsRuPkg.convert

export const useDealsStore = defineStore("deals", () => {
	const deals = ref<Deal[]>([])

	/**
	 * ids сделок в store
	 */
	const storedIds = computed<number[]>(() => deals.value.map((deal) => deal.dealId))

	/**
	 * последняя сделка в store
	 */
	const lastDeal = computed<
		| {
				sales: Deal | undefined
				purchases: Deal | undefined
		  }
		| undefined
	>(() => {
		if (!deals.value?.[0]) return undefined

		let maxDealIdSales = 0
		let maxDealIdPurchases = 0

		deals.value?.forEach((deal) => {
			if (deal.dealId > maxDealIdSales && deal.role === "seller")
				maxDealIdSales = deal.dealId
			if (deal.dealId > maxDealIdPurchases && deal.role === "buyer")
				maxDealIdPurchases = deal.dealId
		})

		return {
			sales: deals.value?.find((deal) => deal.dealId === maxDealIdSales),
			purchases: deals.value?.find((deal) => deal.dealId === maxDealIdPurchases)
		}
	})

	/**
	 * стоймость одного товара
	 */
	const amountPriceInProductItem = () => {
		deals.value?.forEach((deal) => {
			deal.product.productList?.forEach((p: ProductItem) => {
				p.amount = p.price * p.quantity
			})
		})
	}

	/**
	 * стоимость всех товаров
	 */
	const amountPriceInProduct = () => {
		deals.value?.forEach((deal) => {
			deal.product.amountPrice = Number(
				deal.product.productList?.reduce(
					(acc: number, p: ProductItem) => p.amount + acc,
					0
				)
			)
		})
	}

	/**
	 * стоимость всех товаров словами
	 */
	const amountWordProduct = () => {
		deals.value?.forEach((deal) => {
			deal.product.amountWord = numberToWordsRu(deal.product.amountPrice, {
				showNumberParts: {
					fractional: false
				},
				showCurrency: {
					integer: false
				}
			})
		})
	}

	watchEffect(() => {
		amountPriceInProductItem()
		amountPriceInProduct()
		amountWordProduct()
	})

	/**
	 * поиск сделки по id
	 * @param dealId - id сделки
	 * @returns сделка или undefined
	 */
	const findDeal = (dealId: number) => {
		return deals.value?.find((d) => d.dealId === dealId)
	}

	/**
	 * очистка store
	 * @returns void
	 */
	const clearStore = () => {
		deals.value = []
	}

	/**
	 * добавление новой сделки в store
	 * @param newDeal - новая сделка
	 * @returns void
	 */
	const addNewDeal = (newDeal: Deal) => {
		if (!newDeal) return

		const exists = deals.value?.some((d) => d.dealId === newDeal.dealId)

		if (!exists) {
			deals.value?.push(newDeal)
		}
	}

	/**
	 * поиск сделки по номеру заказа
	 * @param dealNumber - номер заказа
	 * @param role - роль (seller или buyer)
	 * @returns сделка или undefined
	 */
	const findDealByDealNumber = (
		dealNumber: string,
		role: "seller" | "buyer"
	) => {
		return deals.value?.find(
			(d) => d.buyerOrderNumber === dealNumber && d.role === role
		)
	}

	/**
	 * добавление нового товара в сделку
	 * @param dealId - id сделки
	 * @param newProduct - новый товар
	 * @returns void
	 */
	const addNewProduct = (dealId: number, newProduct: ProductItem) => {
		const productList = findDeal(dealId)?.product.productList
		if (!productList) return

		productList.push(newProduct)
	}

	/**
	 * редактирование компании продавца
	 * @param dealId - id сделки
	 * @param newSellerCompany - новая компания продавца
	 * @returns void
	 */
	const editSellerCompany = (
		dealId: number,
		newSellerCompany: EditPersonCompany
	) => {
		const sellerCompany = findDeal(dealId)?.seller
		if (!sellerCompany) return

		Object.assign(sellerCompany, newSellerCompany)
	}

	/**
	 * редактирование компании покупателя
	 * @param dealId - id сделки
	 * @param newBuyerCompany - новая компания покупателя
	 * @returns void
	 */
	const editBuyerCompany = (
		dealId: number,
		newBuyerCompany: EditPersonCompany
	) => {
		const buyerCompany = findDeal(dealId)?.buyer
		if (!buyerCompany) return

		Object.assign(buyerCompany, newBuyerCompany)
	}

	/**
	 * редактирование списка товаров в сделке
	 * @param dealId - id сделки
	 * @param newProductList - новый список товаров
	 * @returns void
	 */
	const editProductList = (dealId: number, newProductList: ProductItem[]) => {
		const deal = findDeal(dealId)
		if (!deal) return

		deal.product.productList = [...newProductList]
	}

	/**
	 * редактирование комментариев к сделке
	 * @param dealId - id сделки
	 * @param comments - новые комментарии
	 * @returns void
	 */
	const editProductComments = (dealId: number, comments: string) => {
		const product = findDeal(dealId)?.product
		if (!product) return

		product.comments = comments
	}

	/**
	 * удаление сделки из store
	 * @param dealId - id сделки
	 * @returns void
	 */
	const removeDeal = (dealId: number) => {
		if (!dealId) return
		const deal = findDeal(dealId)
		if (!deal) return

		deals.value = deals.value?.filter((deal: Deal) => deal.dealId !== dealId)
	}

	/**
	 * полное обновление сделки
	 * @param dealId - id сделки
	 * @param seller - компания продавца
	 * @param buyer - компания покупателя
	 * @param newProductList - новый список товаров
	 * @param comments - новые комментарии
	 * @returns void
	 */
	const fullUpdateDeal = async (
		dealId: number,
		seller: EditPersonCompany,
		buyer: EditPersonCompany,
		newProductList: ProductItem[],
		comments?: string
	) => {
		editSellerCompany(dealId, seller)
		editBuyerCompany(dealId, buyer)
		editProductList(dealId, newProductList)

		if (comments !== undefined) {
			editProductComments(dealId, comments)
		}
	}

	return {
		deals,
		storedIds,
		findDealByDealNumber,
		findDeal,
		lastDeal,
		clearStore,
		addNewDeal,
		amountPriceInProductItem,
		amountPriceInProduct,
		amountWordProduct,
		addNewProduct,
		editSellerCompany,
		editBuyerCompany,
		editProductList,
		editProductComments,
		removeDeal,
		fullUpdateDeal
	}
})

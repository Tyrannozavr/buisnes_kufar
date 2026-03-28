import { defineStore } from "pinia"
import type { Company, Deal, ProductItem } from "~/types/dealState"
import numberToWordsRuPkg from "number-to-words-ru"
import type { OfficialBill } from "~/types/bill"

const numberToWordsRu = numberToWordsRuPkg.convert

export const useDealsStore = defineStore("deals", () => {
	const deals = ref<Deal[]>([])

	/**
	 * ids сделок в store
	 */
	const storedIds = computed<number[]>(() =>
		deals.value.map((deal) => deal.dealId)
	)

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
	 * стоимость всех товаров с учетом НДС(всего к оплате)
	 */
	const amountPriceInProductWithoutVat = () => {
		deals.value?.forEach((deal) => {
			if (deal.amountWithVatRate) {
				deal.product.amountPrice = Number(
					deal.product.productList?.reduce((acc: number, p: ProductItem) => {
						return p.amount + (p.amount * (deal.seller.vatRate ?? 0)) / 100 + acc
					}, 0)
				)
			}
		})
	}

	/**
	 * стоимость всех товаров без учета НДС
	 */
	const amountPriceInProduct = () => {
		deals.value?.forEach((deal) => {
			if (!deal.amountWithVatRate) {
				deal.product.amountPrice = Number(
					deal.product.productList?.reduce((acc: number, p: ProductItem) => {
						return p.amount + acc
					}, 0)
				)
			}
		})
	}

	/**
	 * стоимость всех товаров словами
	 */
	const amountWordProduct = () => {
		deals.value?.forEach((deal) => {
			deal.product.amountWord = numberToWordsRu(deal.product.amountPrice, {
				showNumberParts: {
					fractional: true
				},
				convertNumberToWords: {
					fractional: false
				},
				showCurrency: {
					integer: true,
					fractional: true
				}
			})
		})
	}

	watchEffect(() => {
		amountPriceInProductItem()
		amountPriceInProductWithoutVat()
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
	const editSellerCompany = async (
		dealId: number,
		newSellerCompany: Company
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
	const editBuyerCompany = async(
		dealId: number,
		newBuyerCompany: Company
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
	const editProductList = async (
		dealId: number,
		newProductList: ProductItem[]
	) => {
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
	const editProductComments = async (dealId: number, comments: string) => {
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
	 * редактирование списка должностных лиц в счете
	 * @param dealId - id сделки
	 * @param officials - новый список должностных лиц
	 * @returns void
	 */
	const editOfficialsBill = async (
		dealId: number,
		officials: OfficialBill[]
	) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.officials = [...officials]
	}

	/**
	 * обновление даты и номера счёта после createBill
	 * @param dealId - id сделки
	 * @param date - дата счёта (bill_date)
	 * @param number - номер счёта (bill.number)
	 */
	const editBillFields = async (
		dealId: number,
		date: string,
		number: string
	) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.billDate = date
		deal.bill.number = number
	}

	/**
	 * обновление даты договора после createContract
	 * @param dealId - id сделки
	 * @param date - дата договора (contract_date)
	 */
	const editContractDate = async (dealId: number, date: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.contractDate = date
	}

	/**
	 * обновление даты договора поставки после createSupplyContract
	 * @param dealId - id сделки
	 * @param date - дата договора поставки (supply_contracts_date)
	 */
	const editSupplyContractsDate = async (dealId: number, date: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.supplyContractsDate = date
	}

	/**
	 * переключение «Сумма с учётом НДС» для сделки
	 */
	const editAmountWithVatRate = async (dealId: number, value: boolean) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.amountWithVatRate = value
	}

	/**
	 * редактирование суммы без НДС
	 * @param dealId - id сделки
	 * @param amountExclVat - новая сумма без НДС
	 * @returns void
	 */
	const editAmountExclVat = async (dealId: number, amountExclVat: number) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.totalAmountExclVat = amountExclVat
	}

	const editBillReason = async (dealId: number, reason: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.reason = reason
	}

	/**
	 * редактирование срока оплаты в счете
	 * @param dealId - id сделки
	 * @param paymentTerms - новый срок оплаты
	 * @returns void
	 */
	const editPaymentTerms = async (dealId: number, paymentTerms: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.paymentTerms = paymentTerms
	}

	/**
	 * редактирование дополнительной информации в счете
	 * @param dealId - id сделки
	 * @param additionalInfo - новая дополнительная информация
	 * @returns void
	 */
	const editAdditionalInfo = async (dealId: number, additionalInfo: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.additionalInfo = additionalInfo
	}

	/**
	 * редактирование ставки НДС продавца
	 * @param dealId - id сделки
	 * @param vatRate - новая ставка НДС
	 * @returns void
	 */
	const editVatRateSeller = async (dealId: number, vatRate: number) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.seller.vatRate = vatRate
	}

	/**
	 * редактирование суммы НДС
	 * @param dealId - id сделки
	 * @param amountVatRate - новая сумма НДС
	 * @returns void
	 */
	const editAmountVatRate = async (dealId: number, amountVatRate: number) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.product.amountVatRate = amountVatRate
	}

	/**
	 * редактирование условий договора
	 * @param dealId - id сделки
	 * @param contractTerms - новые условия договора
	 * @returns void
	 */
	const editContractTermsContract = async (dealId: number, contractTerms: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom') => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.contractTermsContract = contractTerms
	}

	/**
	 * редактирование текста условий договора
	 * @param dealId - id сделки
	 * @param contractTermsText - новый текст условий договора
	 * @returns void
	 */
	const editContractTermsTextContract = async (dealId: number, contractTermsText: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.contractTermsTextContract = contractTermsText
	}

	/**
	 * редактирование срока оплаты в счете
	 * @param dealId - id сделки
	 * @param paymentTerms - новый срок оплаты
	 * @returns void
	 */
	const editPaymentTermsContract = async (dealId: number, paymentTerms: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.paymentTermsContract = paymentTerms
	}

	/**
	 * редактирование срока поставки в счете
	 * @param dealId - id сделки
	 * @param deliveryTerms - новый срок поставки
	 * @returns void
	 */

	const editDeliveryTermsContract = async (dealId: number, deliveryTerms: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.deliveryTermsContract = deliveryTerms
	}

	/**
	 * редактирование срока оплаты в счете
	 * @param dealId - id сделки
	 * @param paymentTerms - новый срок оплаты
	 * @returns void
	 */
	const editPaymentTermsOffer = async (dealId: number, paymentTerms: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.paymentTermsOffer = paymentTerms
	}

	/**
	 * редактирование срока оплаты в счете
	 * @param dealId - id сделки
	 * @param paymentTerms - новый срок оплаты
	 * @returns void
	 */
	const editContractTermsOffer = async (dealId: number, contractTerms: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom') => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.contractTermsOffer = contractTerms
	}

	/**
	 * редактирование текста условий договора
	 * @param dealId - id сделки
	 * @param contractTermsText - новый текст условий договора
	 * @returns void
	 */
	const editContractTermsTextOffer = async (dealId: number, contractTermsText: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.contractTermsTextOffer = contractTermsText
	}

	/**
	 * редактирование дополнительной информации в счете
	 * @param dealId - id сделки
	 * @param additionalInfo - новая дополнительная информация
	 * @returns void
	 */
	const editAdditionalInfoOffer = async (dealId: number, additionalInfo: string) => {
		const deal = findDeal(dealId)
		if (!deal) return
		deal.bill.additionalInfoOffer = additionalInfo
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
		editAmountExclVat,
		amountPriceInProductWithoutVat,
		amountPriceInProduct,
		amountWordProduct,
		addNewProduct,
		editSellerCompany,
		editBuyerCompany,
		editProductList,
		editProductComments,
		removeDeal,
		editContractDate,
		editSupplyContractsDate,
		//bill
		editBillFields,
		editAmountVatRate,
		editAmountWithVatRate,
		editOfficialsBill,
		editVatRateSeller,
		//bill-payment
		editBillReason,
		editPaymentTerms,
		editAdditionalInfo,
		//bill-contract
		editPaymentTermsContract,
		editDeliveryTermsContract,
		editContractTermsContract,
		editContractTermsTextContract,
		//bill-offer
		editPaymentTermsOffer,
		editContractTermsOffer,
		editContractTermsTextOffer,
		editAdditionalInfoOffer,
	}
})

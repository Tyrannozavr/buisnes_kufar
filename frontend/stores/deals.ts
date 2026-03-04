import { defineStore } from "pinia"
import type { Deal, EditPersonCompany, ProductItem } from "~/types/dealState"
import type {
	BuyerDealResponse,
	DealResponse,
	DealUpdate,
	OrderItemUpdate,
	ProductResponse
} from "~/types/dealResponse"
import numberToWordsRuPkg from "number-to-words-ru"
import { usePurchasesApi } from "~/api/purchases"

const numberToWordsRu = numberToWordsRuPkg.convert

export const useDealsStore = defineStore("deals", () => {
	const deals = ref<Deal[]>([])

	const lastDeal = computed<{
		sales: Deal | undefined,
		purchases: Deal | undefined
	} | undefined>(() => {
		if (!deals.value?.[0]) return undefined

		let maxDealIdSales = 0
		let maxDealIdPurchases = 0

		deals.value?.forEach((deal) => {
			if (deal.dealId > maxDealIdSales && deal.role === "seller") maxDealIdSales = deal.dealId
			if (deal.dealId > maxDealIdPurchases && deal.role === "buyer") maxDealIdPurchases = deal.dealId
		})

		return {
			sales: deals.value?.find((deal) => deal.dealId === maxDealIdSales),
			purchases: deals.value?.find((deal) => deal.dealId === maxDealIdPurchases)
		}
	})

	const findDeal = (dealId: number) => {
		return deals.value?.find((d) => d.dealId === dealId)
	}

	const createBodyForUpdate = (dealId: number): DealUpdate | null => {
		const deal: Deal | undefined = findDeal(dealId)

		if (!deal) return null

		const products = deal.product.productList

		const itemsList: OrderItemUpdate[] = (products ?? []).map(
			(p: ProductItem) => ({
				product_name: p.name.trim() || "—",
				quantity: p.quantity,
				unit_of_measurement: p.units.trim() || "шт",
				price: p.price
			})
		)

		const body: DealUpdate = {
			items: itemsList,
			comments: deal.product.comments ?? undefined
		}

		if (deal.status) body.status = deal.status
		if (deal.contractNumber) body.contract_number = deal.contractNumber
		if (deal.billNumber) body.bill_number = deal.billNumber
		if (deal.supplyContractNumber)
			body.supply_contracts_number = deal.supplyContractNumber

		return body
	}

	const clearStore = () => {
		deals.value = []
	}

	const addNewDeal = (newDeal: Deal) => {
		if (!newDeal) return

		const exists = deals.value?.some((d) => d.dealId === newDeal.dealId)

		if (!exists) {
			deals.value?.push(newDeal)
		}
	}

	const amountPriceInProductItem = () => {
		deals.value?.forEach((deal) => {
			deal.product.productList?.forEach((p: ProductItem) => {
				p.amount = p.price * p.quantity
			})
		})
	}

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

	const findDealByDealNumber = (dealNumber: string, role: "seller" | "buyer") => {
		return deals.value?.find((d) => d.buyerOrderNumber === dealNumber && d.role === role)
	}

	const addNewProduct = (dealId: number, newProduct: ProductItem) => {
		const productList = findDeal(dealId)?.product.productList
		if (!productList) return

		productList.push(newProduct)
	}

	const editSellerCompany = (
		dealId: number,
		newSellerCompany: EditPersonCompany
	) => {
		const sellerCompany = findDeal(dealId)?.seller
		if (!sellerCompany) return

		Object.assign(sellerCompany, newSellerCompany)
	}

	const editBuyerCompany = (
		dealId: number,
		newBuyerCompany: EditPersonCompany
	) => {
		const buyerCompany = findDeal(dealId)?.buyer
		if (!buyerCompany) return

		Object.assign(buyerCompany, newBuyerCompany)
	}

	const editProductList = (dealId: number, newProductList: ProductItem[]) => {
		const deal = findDeal(dealId)
		if (!deal) return

		deal.product.productList = [...newProductList]
	}

	const editProductComments = (dealId: number, comments: string) => {
		const product = findDeal(dealId)?.product
		if (!product) return

		product.comments = comments
	}

	const removeDeal = (dealId: number) => {
		if (!dealId) return

		const deal = findDeal(dealId)
		const { deleteDealById } = usePurchasesApi()

		if (!deal) return

		const index = deals.value?.findIndex((d: Deal) => {
			return d.dealId === deal.dealId
		})

		if (index !== -1 && typeof index !== "undefined") {
			deals.value?.splice(index, 1)
			deleteDealById(dealId)
		}
	}

	const responseToDeal = (dealResponse: DealResponse): Deal => {
		return {
			dealId: dealResponse.id,
			buyerOrderNumber: dealResponse.buyer_order_number,
			sellerOrderNumber: dealResponse.seller_order_number,
			role: dealResponse.role,
			date: dealResponse.created_at,
			product: {
				productList: dealResponse.items.map((item: ProductResponse) => ({
					name: item.product_name,
					article: item.product_article,
					quantity: item.quantity,
					units: item.unit_of_measurement ?? "",
					price: item.price,
					amount: item.amount
				})),
				amountPrice: 0,
				amountWord: "",
				comments: dealResponse.comments ?? ""
			},
			seller: {
				sellerName: dealResponse.seller_company.name,
				companyName: dealResponse.seller_company.company_name,
				phone: dealResponse.seller_company.phone,
				slug: dealResponse.seller_company.slug,
				companyId: dealResponse.seller_company.id,
				email: dealResponse.seller_company.email,
				inn: dealResponse.seller_company.inn,
				legalAddress: dealResponse.seller_company.legal_address
			},
			buyer: {
				buyerName: dealResponse.buyer_company.name,
				companyName: dealResponse.buyer_company.company_name,
				phone: dealResponse.buyer_company.phone,
				slug: dealResponse.buyer_company.slug,
				companyId: dealResponse.buyer_company.id,
				email: dealResponse.buyer_company.email,
				inn: dealResponse.buyer_company.inn,
				legalAddress: dealResponse.buyer_company.legal_address
			},
			status: dealResponse.status,
			billNumber: dealResponse.bill_number || "",
			billDate: dealResponse.bill_date || "",
			contractNumber: dealResponse.contract_number || "",
			contractDate: dealResponse.contract_date || "",
			supplyContractNumber: dealResponse.supply_contracts_number || "",
			supplyContractDate: dealResponse.supply_contracts_date || "",
			closingDocuments: dealResponse.closing_documents || [],
			othersDocuments: dealResponse.others_documents || []
		}
	}

	const getDeals = async () => {
		await clearStore()

		const { getDealById, getBuyerDeals } = usePurchasesApi()
		const buyerDeals = await getBuyerDeals()

		const dealsIds: number[] = [
			...new Set(
				(buyerDeals?.map((deal: BuyerDealResponse) => deal.id) ?? []) as number[]
			)
		]

		for (const dealId of dealsIds) {
			const dealResponse = await getDealById(dealId)
			if (!dealResponse) continue
			addNewDeal(responseToDeal(dealResponse))
		}
	}

	const createNewDealVersion = async (dealId: number) => {
		const { createNewDealVersion } = usePurchasesApi()
		const body = createBodyForUpdate(dealId)
		await createNewDealVersion(dealId, body ?? {})
	}

	const fullUpdateDeal = async (
		dealId: number,
		seller: EditPersonCompany,
		buyer: EditPersonCompany,
		newProductList: ProductItem[],
		comments?: string
	) => {
		amountPriceInProductItem()
		amountPriceInProduct()
		amountWordProduct()
		editSellerCompany(dealId, seller)
		editBuyerCompany(dealId, buyer)
		editProductList(dealId, newProductList)

		if (comments !== undefined) {
			editProductComments(dealId, comments)
		}

		const { updateDealById } = usePurchasesApi()
		const body = createBodyForUpdate(dealId)

		if (!body) return

		await updateDealById(dealId, body)
	}

	return {
		deals,
		findDealByDealNumber,
		findDeal,
		lastDeal,
		createBodyForUpdate,
		clearStore,
		getDeals,
		createNewDealVersion,
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

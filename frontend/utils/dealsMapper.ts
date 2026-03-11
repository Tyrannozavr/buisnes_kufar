import type { DealResponse, DealUpdate, OrderItemUpdate, ProductResponse } from "~/types/dealResponse"
import type { Deal, ProductItem } from "~/types/dealState"
import { useDeals } from '~/composables/useDeals'


export const createBodyForUpdate = (dealId: number): DealUpdate | null => {
	const { findDeal } = useDeals()
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

export const responseToDeal = (dealResponse: DealResponse): Deal => {
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
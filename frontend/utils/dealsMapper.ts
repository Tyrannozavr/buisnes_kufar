import type { OfficialsResponse, DealResponse, DealUpdate, OrderItemUpdate, ProductItemResponse, CompanyInDealResponse } from "~/types/dealResponse"
import type { Deal, ProductItem } from "~/types/dealState"
import type { OfficialBill } from "~/types/bill"
import { useDeals } from '~/composables/useDeals'


export const createBodyForUpdate = (dealId: number): DealUpdate => {
	const { findDeal } = useDeals()
	const deal: Deal | undefined = findDeal(dealId)

	if (!deal) return { updated_at: new Date().toISOString() }

	const seller = deal.seller

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
		comments: deal.product.comments ?? undefined,
		updated_at: new Date().toISOString(),
		amount_with_vat_rate: deal.amountWithVatRate ?? undefined,
		amount_vat_rate: deal.product.amountVatRate ?? undefined,
		seller_company: {
			vat_rate: seller.vatRate ?? 0
		} as CompanyInDealResponse
	}

	if (deal.status) body.status = deal.status
	if (deal.contract.length > 0) body.contract = deal.contract
	// bill всегда с явными строками: undefined в JSON.stringify выкидывается, на бэке payment_terms не приходит
	// и репозиторий не обновляет order.payment_terms (см. update_order: payment_terms is not None).
	if (deal.bill) {
		body.bill = {
			number: deal.bill.number ?? "",
			reason: deal.bill.reason ?? "",
			payment_terms: String(deal.bill.paymentTerms ?? ""),
			additional_info: deal.bill.additionalInfo ?? "",
			contract_terms: deal.bill.contractTerms ?? "standard-delivery-supplier",
			contract_terms_text: deal.bill.contractTermsText ?? "",
			officials: deal.bill.officials.map((official: OfficialBill) => ({
				id: official.id,
				full_name: official.name,
				position: official.position
			}) satisfies OfficialsResponse)
		}
	}
	if (deal.contract) body.contract = deal.contract
	if (deal.supplyContracts) body.supply_contracts = deal.supplyContracts
	if (deal.closingDocuments) body.closing_documents = deal.closingDocuments
	if (deal.othersDocuments) body.others_documents = deal.othersDocuments

	return body
}

export const responseToDeal = (dealResponse: DealResponse): Deal => {
	return {
		dealId: dealResponse.id,
		buyerOrderNumber: dealResponse.buyer_order_number,
		sellerOrderNumber: dealResponse.seller_order_number,
		role: dealResponse.role as "buyer" | "seller",
		date: dealResponse.created_at,
		product: {
			productList: dealResponse.items.map((item: ProductItemResponse) => ({
				name: item.product_name,
				article: item.product_article,
				quantity: item.quantity,
				units: item.unit_of_measurement ?? "",
				price: item.price,
				amount: item.amount
			})),
			amountPrice: dealResponse.amount_with_vat_rate
				? dealResponse.total_amount +
					(dealResponse.total_amount * (dealResponse.seller_company.vat_rate ?? 0)) /
						100
				: dealResponse.total_amount,
			amountVatRate: dealResponse.amount_vat_rate ?? 0,
			amountWord: "",
			comments: dealResponse.comments ?? ""
		},
		seller: {
			ownerName: dealResponse.seller_company.owner_name,
			companyName: dealResponse.seller_company.company_name,
			phone: dealResponse.seller_company.phone,
			slug: dealResponse.seller_company.slug,
			companyId: dealResponse.seller_company.company_id,
			email: dealResponse.seller_company.email,
			inn: dealResponse.seller_company.inn,
			legalAddress: dealResponse.seller_company.legal_address,
			index: dealResponse.seller_company.index,
			kpp: dealResponse.seller_company.kpp,
			accountNumber: dealResponse.seller_company.account_number,
			correspondentBankAccount: dealResponse.seller_company.correspondent_bank_account,
			bankName: dealResponse.seller_company.bank_name,
			bic: dealResponse.seller_company.bic,
			vatRate: dealResponse.seller_company.vat_rate
		},
		buyer: {
			ownerName: dealResponse.buyer_company.owner_name,
			companyName: dealResponse.buyer_company.company_name,
			phone: dealResponse.buyer_company.phone,
			slug: dealResponse.buyer_company.slug,
			companyId: dealResponse.buyer_company.company_id,
			email: dealResponse.buyer_company.email,
			inn: dealResponse.buyer_company.inn,
			legalAddress: dealResponse.buyer_company.legal_address,
			index: dealResponse.buyer_company.index,
			kpp: dealResponse.buyer_company.kpp,
			accountNumber: dealResponse.buyer_company.account_number,
			correspondentBankAccount: dealResponse.buyer_company.correspondent_bank_account,
			bankName: dealResponse.buyer_company.bank_name,
			bic: dealResponse.buyer_company.bic,
			vatRate: dealResponse.buyer_company.vat_rate
		},
		status: dealResponse.status,
		amountWithVatRate: dealResponse.amount_with_vat_rate as boolean,
		bill: {
			number: dealResponse.bill.number,
			reason: dealResponse.bill.reason,
			paymentTerms: dealResponse.bill.payment_terms,
			additionalInfo: dealResponse.bill.additional_info,
			contractTerms: dealResponse.bill.contract_terms ?? "standard-delivery-supplier",
			contractTermsText: dealResponse.bill.contract_terms_text ?? "",
			officials: dealResponse.bill.officials.map(
				(official: OfficialsResponse) => ({
					id: official.id,
					name: official.full_name,
					position: official.position
				})
			)
		},
		billDate: dealResponse.bill_date,
		contract: dealResponse.contract || [],
		contractDate: dealResponse.contract_date,
		supplyContracts: dealResponse.supply_contracts || [],
		supplyContractsDate: dealResponse.supply_contracts_date,
		closingDocuments: dealResponse.closing_documents || [],
		othersDocuments: dealResponse.others_documents || []
	}
}
import type { DealResponse, DealUpdate, OrderItemUpdate, ProductItemResponse, CompanyInDealResponse, OfficialsResponse } from "~/types/dealResponse"
import type { Deal, ProductItem, SupplyContract, Official } from "~/types/dealState"
import { useDeals } from '~/composables/useDeals'
import { normalizeSpecificationNumber } from '~/utils/normalize'


const mapOfficialForUpdate = (
	official: Official,
	companyId: number,
): OfficialsResponse => ({
	id: official.id,
	company_id: companyId,
	full_name: official.name,
	position: official.position,
	is_base: official.isBase,
	base_document: official.baseDocument,
	base_document_name: official.baseDocumentName,
})

const mapOfficialsForDeal = (official: OfficialsResponse): Official => ({
	id: official.id,
	companyId: official.company_id,
	name: official.full_name,
	position: official.position,
	isBase: official.is_base,
	baseDocument: official.base_document,
	baseDocumentName: official.base_document_name
})

const optionalDateField = (value: string | undefined | null): string | undefined =>
	value?.trim() ? value : undefined


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
	if (deal.contract.length > 0) {
		body.contract = deal.contract.map((item) => {
			const contract = item as { number?: string; date?: string }
			return {
				number: contract.number,
				...(optionalDateField(contract.date) ? { date: contract.date } : {}),
			}
		})
	}
	if (deal.bill) {
		body.bill = {
			number: deal.bill.number ?? "",
			reason: deal.bill.reason ?? "",
			//bill-payment
			additional_info: deal.bill.additionalInfo ?? "",
			payment_terms: String(deal.bill.paymentTerms ?? ""),
			//bill-contract
			delivery_terms_contract: String(deal.bill.deliveryTermsContract ?? ""),
			payment_terms_contract: String(deal.bill.paymentTermsContract ?? ""),
			contract_terms_contract: deal.bill.contractTermsContract ?? "standard-delivery-supplier",
			contract_terms_text_contract: deal.bill.contractTermsTextContract ?? "",
			//bill-offer
			payment_terms_offer: String(deal.bill.paymentTermsOffer ?? ""),
			contract_terms_offer: deal.bill.contractTermsOffer ?? "standard-delivery-supplier",
			contract_terms_text_offer: deal.bill.contractTermsTextOffer ?? "",
			additional_info_offer: deal.bill.additionalInfoOffer ?? "",
			officials: deal.bill.officials.map((official: Official) =>
				mapOfficialForUpdate(official, seller.companyId ?? 0),
			),
		}
	}
	if (deal.supplyContract) {
		const specificationDate = optionalDateField(deal.supplyContract.specificationDate)
		const templateSupplyContract = deal.supplyContract.templateSupplyContract
		const templateSpecification = deal.supplyContract.templateSpecification
		const specificationNumber = normalizeSpecificationNumber(deal.supplyContract.specificationNumber)
		body.supply_contract = {
			number: deal.supplyContract.number,
			officials: deal.supplyContract.officialsSeller.map((official: Official) =>
				mapOfficialForUpdate(official, seller.companyId ?? 0),
			),
			specification_number: specificationNumber || undefined,
			...(specificationDate ? { specification_date: specificationDate } : {}),
			terms_text: deal.supplyContract.supplyContractText ?? '',
			specification_text: deal.supplyContract.specificationText ?? '',
			...(templateSupplyContract
				? { template_supply_contract: String(templateSupplyContract) }
				: {}),
			...(templateSpecification
				? { template_specification: String(templateSpecification) }
				: {}),
			supplier_details_check: deal.supplyContract.supplierDetailsCheck,
			buyer_details_check: deal.supplyContract.buyerDetailsCheck,
			cover_letter_check: deal.supplyContract.coverLetterCheck,
		}
	}
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
		totalAmountExclVat: dealResponse.total_amount_excl_vat ?? 0,
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
			amountWord: dealResponse.total_amount_word ?? "",
			comments: dealResponse.comments ?? ""
		},
		seller: {
			ownerName: dealResponse.seller_company.owner_name,
			companyName: dealResponse.seller_company.company_name,
			companyType: dealResponse.seller_company.company_type,
			fullName: dealResponse.seller_company.full_name,
			city: dealResponse.seller_company.city,
			phone: dealResponse.seller_company.phone,
			slug: dealResponse.seller_company.slug,
			companyId: dealResponse.seller_company.company_id,
			email: dealResponse.seller_company.email,
			inn: dealResponse.seller_company.inn,
			ogrn: dealResponse.seller_company.ogrn,
			legalAddress: dealResponse.seller_company.legal_address,
			productionAddress: dealResponse.seller_company.production_address,
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
			companyType: dealResponse.buyer_company.company_type,
			fullName: dealResponse.buyer_company.full_name,
			city: dealResponse.buyer_company.city,
			phone: dealResponse.buyer_company.phone,
			slug: dealResponse.buyer_company.slug,
			companyId: dealResponse.buyer_company.company_id,
			email: dealResponse.buyer_company.email,
			inn: dealResponse.buyer_company.inn,
			ogrn: dealResponse.buyer_company.ogrn,
			legalAddress: dealResponse.buyer_company.legal_address,
			productionAddress: dealResponse.buyer_company.production_address,
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
			paymentTerms:
				dealResponse.bill.payment_terms ??
				dealResponse.bill.payment_terms_contract ??
				"",
			additionalInfo: dealResponse.bill.additional_info,
			paymentTermsContract: dealResponse.bill.payment_terms_contract ?? "",
			deliveryTermsContract: dealResponse.bill.delivery_terms_contract ?? "",
			contractTermsContract:
				dealResponse.bill.contract_terms_contract ?? "standard-delivery-supplier",
			contractTermsTextContract:
				dealResponse.bill.contract_terms_text_contract ?? "",
			paymentTermsOffer: dealResponse.bill.payment_terms_offer ?? "",
			contractTermsOffer:
				dealResponse.bill.contract_terms_offer ?? "standard-delivery-supplier",
			contractTermsTextOffer:
				dealResponse.bill.contract_terms_text_offer ?? "",
			additionalInfoOffer: dealResponse.bill.additional_info_offer ?? "",
			officials: dealResponse.bill.officials.map(official => mapOfficialsForDeal(official))
		},
		billDate: dealResponse.bill_date,
		contract: dealResponse.contract || [],
		contractDate: dealResponse.contract_date,
		supplyContract: {
			entityId: dealResponse.supply_contract.entity_id,
			specificationEntityId: dealResponse.supply_contract.specification_entity_id,
			entityDate: dealResponse.supply_contract_date || undefined,
			supplyContractText: dealResponse.supply_contract.supply_contract_text ?? '',
			specificationText: dealResponse.supply_contract.specification_text ?? '',
			number: dealResponse.supply_contract.number,
			officialsSeller: (
				dealResponse.supply_contract.officials
				?? dealResponse.supply_contract.officialsSeller
				?? []
			).map(official => mapOfficialsForDeal(official)),
			specificationNumber: normalizeSpecificationNumber(dealResponse.supply_contract.specification_number),
			specificationDate: dealResponse.supply_contract.specification_date ?? '',
			templateSupplyContract: dealResponse.supply_contract.template_supply_contract ?? '',
			templateSpecification: dealResponse.supply_contract.template_specification ?? '',
			supplierDetailsCheck: dealResponse.supply_contract.supplier_details_check,
			buyerDetailsCheck: dealResponse.supply_contract.buyer_details_check,
			coverLetterCheck: dealResponse.supply_contract.cover_letter_check
		} satisfies SupplyContract,
		supplyContractDate: dealResponse.supply_contract_date,
		closingDocuments: dealResponse.closing_documents || [],
		othersDocuments: dealResponse.others_documents || []
	}
}
import type { Company } from "./dealState"
import type { ProductsInOrder } from "./order"

export interface OfficialBill {
	id: number
	name: string
	position: string
}

export interface BillData {
	number: string
	dealId: number
	amount: number
	amountVatRate: number
	amountWord: string
	date: string
	reason: string
	paymentTerms: string
	deliveryTerms: string
	additionalInfo: string
	contractTerms: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom'
	contractTermsText: string
	products: ProductsInOrder[]
	seller: Company
	buyer: Company
	officials: OfficialBill[]
}

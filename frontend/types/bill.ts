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
	amountExclVat: number
	amountVatRate: number
	amountWord: string
	date: string
	reason: string
	products: ProductsInOrder[]
	seller: Company
	buyer: Company
	officials: OfficialBill[]

	//bill-payment
	paymentTerms: string
	additionalInfo: string

	//bill-contract
	paymentTermsContract: string
	contractTermsContract: "standard-delivery-supplier" | "standard-delivery-buyer" | "custom"
	deliveryTermsContract: string
	contractTermsTextContract: string
	
	//bill-offer
	paymentTermsOffer: string
	contractTermsOffer: "standard-delivery-supplier" | "standard-delivery-buyer" | "custom"
	contractTermsTextOffer: string
	additionalInfoOffer: string
}

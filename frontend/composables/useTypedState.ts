import type { Official } from "~/types/dealState"
import type { SupplyContractData } from "~/types/supplyContract"

//From constant/keys
interface StateMap {
	//Editor
	saveState: boolean
	isDisabled: boolean
	clearState: boolean
	removeDealState: boolean
	activeTab: "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7"
	loadDealTrigger: number
	orderChangeDiff: import("~/types/dealResponse").DealOrderChangeDiff | null
	billAwaitingFill: boolean

	//bill
	billType: { value: "bill" | "bill-contract" | "bill-offer"; label: string }
	reasonCheck: boolean
	vatRateCheck: boolean
	vatRate: number
	
	//bill-payment(счет-оплата)
	paymentTerms: string
	paymentTermsCheck: boolean
	additionalInfoCheck: boolean

	//bill-contract
	paymentTermsContract: string
	deliveryTermsContract: string
	contractTermsContract: { value: "standard-delivery-supplier" | "standard-delivery-buyer" | "custom"; label: string }
	contractTermsTextContract: string
	paymentTermsCheckContract: boolean
	deliveryTermsCheckContract: boolean
	contractTermsCheckContract: boolean
	
	//bill-offer
	paymentTermsOffer: string
	contractTermsOffer: { value: "standard-delivery-supplier" | "standard-delivery-buyer" | "custom"; label: string }
	contractTermsTextOffer: string
	contractTermsCheckOffer: boolean
	paymentTermsCheckOffer: boolean
	additionalInfoCheckOffer: boolean

	//supply contract
	coverLetterCheck: boolean
	supplierDetailsCheck: boolean
	buyerDetailsCheck: boolean
	supplyContractType: "supplyContract" | "specification"
	supplyContractOfficialsSeller: Official[] | []
	supplyContractTableData: {
		products: SupplyContractData['products']
		amount: SupplyContractData['amount'],
		amountExclVat: SupplyContractData['amountExclVat'],
		amountVatRate: SupplyContractData['amountVatRate'],
	}
	supplyContractSlotRevision: number
	supplyContractPreviewElement: HTMLElement | null
	
	//TemplateElement
	htmlOrder: HTMLElement | null
	htmlBill: HTMLElement | null
	htmlSupplyContract: string | null
	htmlSpecification: string | null
	htmlDogovorUslug: HTMLElement | null
}

export function useTypedState<T extends keyof StateMap>(
	key: T, 
	defaultValue?: () => Ref<StateMap[T]>
) {
	return useState<StateMap[T]>(key, defaultValue)
}
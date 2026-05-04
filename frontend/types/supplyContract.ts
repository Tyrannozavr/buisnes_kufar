import type { ProductsInOrder } from "./order"
import type { Company } from "./dealState"

export interface OfficialSupplyContract {
	id: number
	name: string
	position: string
	isBase: boolean
	baseDocument: string
	baseDocumentName: string
}

export interface SupplyContractData {
	number: string
	date: string
	specificationNumber: string
	specificationDate: string

	seller: Company
	buyer: Company

	officials: OfficialSupplyContract[]
	products: ProductsInOrder[]

	amount: number
	amountExclVat: number
	amountVatRate: number
	amountWord: string

	templateSupplyContract: string
	templateSpecification: string
}
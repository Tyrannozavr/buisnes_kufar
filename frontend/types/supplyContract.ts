import type { ProductsInOrder } from "./order"
import type { Company, Official } from "./dealState"


export interface SupplyContractData {
	dealId: number
	number: string
	date: string
	specificationNumber: string
	specificationDate: string

	seller: Company
	buyer: Company

	officialsSeller: Official[]
	products: ProductsInOrder[]

	amount: number
	amountExclVat: number
	amountVatRate: number
	amountWord: string

	templateSupplyContract: string
	templateSpecification: string
}
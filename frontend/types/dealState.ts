import type { OfficialBill } from "./bill";
import type { OfficialSupplyContract } from "./supplyContract";

export interface Company {
  ownerName?: string;
	companyName?: string;
	companyType?: string;
  slug?: string;
  companyId?: number;
  phone?: string;
  email?: string;
	legalAddress?: string; // Юридический адрес
	productionAddress?: string; // Адрес производства
	index?: string; // Индекс
  inn?: number; // ИНН
	kpp?: string; // КПП
	ogrn?: string; // ОГРН
	accountNumber?: string; // Расчетный счет
	correspondentBankAccount?: string; // Корреспондентский счет
	bankName?: string; // Наименование банка
	bic?: string; // БИК
	vatRate?: number; // Ставка НДС
}

export interface ProductItem {
  name: string;
  article: string;
  quantity: number;
  units: string;
  price: number;
  amount: number;
}

export interface Product {
	productList: ProductItem[]
	amountPrice: number 
	amountVatRate: number
	amountWord: string
	comments?: string 
}

export interface Bill {
	number: string
	reason: string
	officials: OfficialBill[]

	//bill-payment
	paymentTerms: string
	additionalInfo: string

	//bill-contract
	paymentTermsContract: string
	deliveryTermsContract: string
	contractTermsContract: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom' 
	contractTermsTextContract: string

	//bill-offer
	paymentTermsOffer: string
	contractTermsOffer: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom' 
	contractTermsTextOffer: string
	additionalInfoOffer: string
}

export interface SupplyContract {
	number: string
	officials: OfficialSupplyContract[]
	specificationNumber: string
	specificationDate: string
	templateSupplyContract: string
	templateSpecification: string
	supplierDetailsCheck: boolean
	buyerDetailsCheck: boolean
	coverLetterCheck: boolean
}

export interface Deal {
  dealId: number;
  buyerOrderNumber: string;
  sellerOrderNumber: string;
  role: "buyer" | "seller";
  product: Product;
  date: string;
  seller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная"
	amountWithVatRate: boolean
	totalAmountExclVat: number
	bill: Bill
	billDate: string
  contract: unknown[]
  contractDate: string
  supplyContract: SupplyContract
  supplyContractDate: string
  closingDocuments: unknown[]
  othersDocuments: unknown[]
}

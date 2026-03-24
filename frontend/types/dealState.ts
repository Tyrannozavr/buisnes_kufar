import type { OfficialBill } from "./bill";

export interface Company {
  ownerName?: string;
	companyName?: string;
  slug?: string;
  companyId?: number;
  phone?: string;
  email?: string;
	legalAddress?: string; // Юридический адрес
	index?: string; // Индекс
  inn?: number; // ИНН
	kpp?: string; // КПП
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
	paymentTerms: string
	deliveryTerms: string
	additionalInfo: string
	contractTerms: 'standard-delivery-supplier' | 'standard-delivery-buyer' | 'custom' 
	contractTermsText: string
	officials: OfficialBill[]
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
	bill: Bill
	billDate: string
  contract: unknown[]
  contractDate: string
  supplyContracts: unknown[]
  supplyContractsDate: string
  closingDocuments: unknown[]
  othersDocuments: unknown[]
}

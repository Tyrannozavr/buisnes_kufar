export interface Person {
  name: string;
  mobileNumber?: string;
  companyName: string;
  legalAddress?: string;
  inn: number;
}

export interface Company {
  sellerName?: string;
  buyerName?: string;
  companyName?: string;
  slug?: string;
  companyId: number;
  inn?: string;
  phone?: string;
  email?: string;
  legalAddress?: string;
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
	amountWord: string
	comments?: string 
}

export interface Bill {
	number: string
	ofpCompany: string
	bik: string
	bankName: string
	accountNumber: string
	inn: string
	kpp: string
	recipient: string
	companyName: string
	supplier: string
	buyer: string
	reason: string
	person1: string
	person2: string
	person3: string
}

export interface Deal {
  dealId: number;
  buyerOrderNumber?: string;
  sellerOrderNumber?: string;
  role?: "buyer" | "seller";
  product: Product;
  date: string;
  seller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная"
  bill?: Bill
  contractNumber?: string
  supplyContractNumber?: string
  closingDocuments?: unknown[]
  othersDocuments?: unknown[]
}

export interface EditPersonCompany {
  name?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}

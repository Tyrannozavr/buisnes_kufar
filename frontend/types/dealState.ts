export interface Person {
  name: string;
  mobileNumber?: string;
  companyName: string;
  legalAddress?: string;
  inn: number;
}

export interface Company {
  slug: string;
  name: string;
  phone: string;
  legalAddress: string;
  inn: string;
}

export interface Product {
  name: string;
  article: string;
  quantity: number;
  units: string;
  price: number;
  amount: number;
	type: string
}

export interface Goods {
	goodsList: Product[]
	amountPrice: number 
	amountWord: string
	comments?: string 
}

export interface Services {
	servicesList: Product[]
	amountPrice: number 
	amountWord: string
	comments?: string 
}

export interface GoodsDeal {
  dealId: number;
  buyerOrderNumber?: string;
  sellerOrderNumber?: string;
  goods: Goods;
  date: string;
  saller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная";
  bill?: string
  supplyContract?: string
  closingDocuments?: string
  othersDocuments?: string
}

export interface ServicesDeal {
  dealId: number;
  buyerOrderNumber?: string;
  sellerOrderNumber?: string;
  services: Services;
  date: string;
  saller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная";
  bill?: string
	contract?: string
	closingDocuments?: string
  othersDocuments?: string
}

export interface EditPersonDeal {
  name?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}

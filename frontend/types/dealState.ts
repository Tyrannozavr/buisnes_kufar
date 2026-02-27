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

export interface GoodsDeal {
  dealId: number;
  buyerOrderNumber?: string;
  sellerOrderNumber?: string;
  goods: Goods;
  date: string;
  seller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная"
  billNumber?: string
  billDate?: string
  contractNumber?: string
  contractDate?: string
  supplyContractNumber?: string
  supplyContractDate?: string
  closingDocuments?: unknown[]
  othersDocuments?: unknown[]
}

export interface EditPersonDeal {
  name?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}

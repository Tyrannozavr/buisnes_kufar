export interface Person {
  name: string;
  mobileNumber?: string;
  companyName: string;
  legalAddress?: string;
  inn: number;
}

export interface Product {
  name: string;
  article: number;
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
	amount: number 
	amountWord: string
	comments?: string 
}

export interface GoodsDeal {
  dealNumber: number;
  goods: Goods;
  date: string;
  saller: Person;
  buyer: Person;
  state?: string;
  bill?: string
  supplyContract?: string
  accompanyingDocuments?: string
  invoice?: string
  othersDocuments?: string
}

export interface ServicesDeal {
  dealNumber: number;
  services: Services;
  date: string;
  saller: Person;
  buyer: Person;
  state?: string;
  bill?: string
	contract?: string
	act?: string
  invoice?: string
  othersDocument?: string
}

export interface EditPersonDeal {
  name?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}
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
  buyerOrderNumber: string;
  goods: Goods;
  date: string;
  saller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная";
  bill?: string
  supplyContract?: string
  accompanyingDocuments?: string
  invoice?: string
  othersDocuments?: string
}

export interface ServicesDeal {
  dealId: number;
  buyerOrderNumber: string;
  services: Services;
  date: string;
  saller: Company;
  buyer: Company;
  status: "Активная" | "Завершенная";
  bill?: string
	contract?: string
	act?: string
  invoice?: string
  othersDocuments?: string
}

export interface EditPersonDeal {
  name?: string;
  mobileNumber?: string;
  companyName?: string;
  legalAddress?: string;
  inn?: number;
}

export interface DealPurchaseResponse {
  buyer_company_id: number;
  buyer_order_number: string;
  created_at: string;
  deal_type: "Товары" | "Услуги";
  id: number;
  seller_company_id: number;
  seller_order_number: string;
  status: "Активная" | "Завершенная";
  supplier_inn: string;
  supplier_name: string;
  supplier_phone: string;
  total_amount: number;
  updated_at: string;
}

export interface ProductResponse {
  product_name: string;
  product_slug: string;
  product_description?: string;
  product_article: string;
  product_type: string;
  logo_url?: string;
  quantity: number;
  unit_of_measurement?: string;
  price: number;
  position: number;
  id: number;
  order_id: number;
  amount: number;
  created_at: string;
  updated_at: string;
}

export interface DealResponse { 
  id: number,
  buyer_company_id: number,
  seller_company_id: number,
  buyer_order_number: string,
  seller_order_number: string,
  status: "Активная" | "Завершенная",
  deal_type: "Товары" | "Услуги",
  total_amount: number,
  comments: string,
  invoice_number: string,
  contract_number: string,
  invoice_date: string,
  contract_date: string,
  created_at: string,
  updated_at: string,
  items: [
    ProductResponse[]
  ],
  buyer_company: any,
  seller_company: any
}
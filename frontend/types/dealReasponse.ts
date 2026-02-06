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
  id: number;
  buyer_company_id: number;
  seller_company_id: number;
  buyer_order_number: string;
  seller_order_number: string;
  status: "Активная" | "Завершенная";
  deal_type: "Товары" | "Услуги";
  total_amount: number;
  comments: string;
  invoice_number: string;
  contract_number: string;
  invoice_date: string;
  contract_date: string;
  created_at: string;
  updated_at: string;
  items: [ProductResponse[]];
  buyer_company: any;
  seller_company: any;
}

export interface BuyerDealResponse {
  id: number,
  buyer_company_id: number,
  seller_company_id: number,
  buyer_order_number: string,
  seller_order_number: string,
  status: "Активная" | "Завершенная",
  deal_type: "Товары" | "Услуги",
  total_amount: number,
  created_at: string,
  updated_at: string,
  supplier_name: string,
  supplier_inn: string,
  supplier_phone: string
}

export interface SellerDealResponse {
  id: number,
  buyer_company_id: number,
  seller_company_id: number,
  buyer_order_number: string,
  seller_order_number: string,
  status: "Активная" | "Завершенная",
  deal_type: "Товары" | "Услуги",
  total_amount: number,
  created_at: string,
  updated_at: string,
  buyer_name: string,
  buyer_inn: string,
  buyer_phone: string 
}
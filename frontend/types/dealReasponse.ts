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

export interface CompanyInDealResponse {
  name: string; // имя владельца компании
  company_name: string; // название компании
  slug: string;
  id: number;
  inn: string;
  phone: string;
  email: string;
  legal_address: string;
}

export interface OrderItemUpdate {
  product_name?: string;
  quantity: number;
  unit_of_measurement?: string;
  price?: number;
  article?: string;
}

export interface DealUpdate {
  status?: "Активная" | "Завершенная";
  items?: OrderItemUpdate[];
  comments?: string;
  contract_number?: string | null;
  bill_number?: string | null;
  bill_date?: string | null;
  supply_contracts_number?: string | null;
  supply_contracts_date?: string | null;
  buyer_order_date?: string | null;
  seller_order_date?: string | null;
}

export interface DealResponse {
  id: number;
  version: number;
  buyer_company_id: number;
  seller_company_id: number;
  buyer_order_number: string;
  seller_order_number: string;
  status: "Активная" | "Завершенная";
  deal_type: "Товары" | "Услуги";
  total_amount: number;
  comments: string;
  buyer_order_date: string | null;
  seller_order_date: string | null;
  contract_number: string | null;
  contract_date: string | null;
  bill_number: string | null;
  bill_date: string | null;
  supply_contracts_number: string | null;
  supply_contracts_date: string | null;
  closing_documents: unknown[];
  others_documents: unknown[];
  created_at: string;
  updated_at: string;
  items: [ProductResponse[]];
  buyer_company: CompanyInDealResponse;
  seller_company: CompanyInDealResponse;
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
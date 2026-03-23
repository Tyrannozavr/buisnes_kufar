export interface DealPurchaseResponse {
  buyer_company_id: number;
  buyer_order_number: string;
  created_at: string;
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

export interface ProductItemResponse {
	product_name: string
	product_slug: string
	product_description?: string
	product_article: string
	logo_url?: string
	quantity: number
	unit_of_measurement?: string
	price: number
	position: number
	id: number
	order_id: number
	amount: number
	created_at: string
	updated_at: string
}

export interface CompanyInDealResponse {
	owner_name?: string // имя владельца компании
	company_name: string
	slug: string
	company_id: number
	phone: string
	email: string
	legal_address: string // Юридический адрес
	index: string // Индекс
	inn: number // ИНН
	kpp: string // КПП
	account_number: string // Расчетный счет
	correspondent_bank_account: string // Корреспондентский счет
	bank_name: string // Наименование банка
	bic: string // БИК
	vat_rate: number // Ставка НДС 0, 10, 20
}

export interface OrderItemUpdate {
  product_name?: string;
  quantity: number;
  unit_of_measurement?: string;
  price?: number;
  article?: string;
}

export interface DealUpdate {
	status?: "Активная" | "Завершенная"
	items?: OrderItemUpdate[]
	comments?: string
	updated_at: string
	total_amount?: number // общая сумма сделки c учетом ндс
	amount_vat_rate?: number // общая сумма НДС
	amount_with_vat_rate?: boolean
	bill?: BillResponse
	bill_date?: string
	contract?: unknown[]
	contract_date?: string
	supply_contracts?: unknown[]
	supply_contracts_date?: string
	closing_documents?: unknown[]
	others_documents?: unknown[]
	buyer_company?: CompanyInDealResponse
	seller_company?: CompanyInDealResponse
}

export interface BillResponse {
	number: string
	reason: string
	payment_terms: string
	additional_info: string
	officials: OfficialsResponse[]
}

export interface OfficialsResponse {
	id: number
	full_name: string
	position: string
}

export interface DealResponse {
	id: number
	version: number
	role: "buyer" | "seller"
	buyer_company_id: number
	seller_company_id: number
	buyer_order_number: string
	seller_order_number: string
	status: "Активная" | "Завершенная"
	created_at: string
	updated_at: string
	total_amount: number
	amount_vat_rate?: number
	amount_with_vat_rate: boolean
	comments: string
	bill: BillResponse
	bill_date: string
	contract: unknown[]
	contract_date: string
	supply_contracts: unknown[]
	supply_contracts_date: string
	closing_documents: unknown[]
	others_documents: unknown[]
	items: ProductItemResponse[]
	buyer_company: CompanyInDealResponse
	seller_company: CompanyInDealResponse
}

export interface BuyerDealResponse {
  id: number,
  buyer_company_id: number,
  seller_company_id: number,
  buyer_order_number: string,
  seller_order_number: string,
  status: "Активная" | "Завершенная",
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
  total_amount: number,
  created_at: string,
  updated_at: string,
  buyer_name: string,
  buyer_inn: string,
  buyer_phone: string 
}

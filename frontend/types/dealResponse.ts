export interface OfficialsResponse {
	id: number
	company_id: number
	full_name: string
	position: string
	is_base: boolean
	base_document: string
	base_document_name: string
}

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
	company_type: string
	full_name?: string
	city?: string
	slug: string
	company_id: number
	phone: string
	email: string
	legal_address: string // Юридический адрес
	production_address: string // Адрес производства
	index: string // Индекс
	inn: number // ИНН
	ogrn?: string // ОРГН
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
	supply_contract?: SupplyContractUpdate
	supply_contract_date?: string
	closing_documents?: unknown[]
	others_documents?: unknown[]
	buyer_company?: CompanyInDealResponse
	seller_company?: CompanyInDealResponse
}

export interface BillResponse {
	number: string
	reason: string
	officials: OfficialsResponse[]
	
	// bill-payment
	payment_terms?: string
	additional_info: string

	// bill-contract
	payment_terms_contract: string
	delivery_terms_contract: string
	contract_terms_contract:
		| "standard-delivery-supplier"
		| "standard-delivery-buyer"
		| "custom"
	contract_terms_text_contract: string

	// bill-offer
	payment_terms_offer: string
	contract_terms_offer:
		| "standard-delivery-supplier"
		| "standard-delivery-buyer"
		| "custom"
	contract_terms_text_offer: string
	additional_info_offer: string
}

export interface SupplyContractUpdate {
	number: string
	officials: OfficialsResponse[]
	specification_number?: string
	specification_date?: string
	terms_text?: string
	specification_text?: string
	template_supply_contract?: string
	template_specification?: string
	supplier_details_check?: boolean
	buyer_details_check?: boolean
	cover_letter_check?: boolean
}

export interface SupplyContractResponse {
	entity_id?: number
	specification_entity_id?: number
	number: string
	/** Ответ API */
	officials?: OfficialsResponse[]
	/** @deprecated legacy alias с фронта */
	officialsSeller?: OfficialsResponse[]
	specification_number: string
	specification_date: string
	template_supply_contract: string
	template_specification: string
	supply_contract_text?: string
	specification_text?: string
	supplier_details_check: boolean
	buyer_details_check: boolean
	cover_letter_check: boolean
}

/** Отдельная сущность договора поставки — см. types/supplyContractEntity.ts */
export type { SupplyContractEntityResponse } from './supplyContractEntity'

export interface OrderLineChange {
	status: "added" | "removed" | "modified"
	match_key: string
	product_name?: string | null
	product_article?: string | null
	quantity?: number | null
	unit_of_measurement?: string | null
	price?: number | null
	amount?: number | null
	changed_fields: string[]
}

export interface DealOrderChangeDiff {
	baseline_version: number
	proposed_version: number
	comments_changed: boolean
	total_amount_changed: boolean
	items: OrderLineChange[]
}

export interface DealChangeReviewResponse {
	has_pending_changes: boolean
	can_respond: boolean
	is_proposer: boolean
	proposed_by_company_id: number | null
	version: number
	diff?: DealOrderChangeDiff | null
}

export interface DealResponse {
	id: number
	version: number
	role: "buyer" | "seller"
	buyer_company_id: number
	seller_company_id: number
	buyer_order_number: string
	seller_order_number: string
	deal_type?: 'Товары' | 'Услуги'
	status: "Активная" | "Завершенная"
	created_at: string
	updated_at: string
	total_amount: number
	/** Сумма позиций без НДС */
	total_amount_excl_vat?: number
	/** Сумма total_amount прописью (рубли/копейки), только с сервера */
	total_amount_word: string
	amount_vat_rate?: number
	amount_with_vat_rate: boolean
	comments: string
	bill: BillResponse
	bill_date: string
	contract: unknown[]
	contract_date: string
	supply_contract: SupplyContractResponse
	supply_contract_date: string
	closing_documents: unknown[]
	others_documents: unknown[]
	items: ProductItemResponse[]
	buyer_company: CompanyInDealResponse
	seller_company: CompanyInDealResponse
}

export interface CheckoutResponse {
	deals: DealResponse[]
}

export interface BuyerDealResponse {
  id: number,
  buyer_company_id: number,
  seller_company_id: number,
  buyer_order_number: string,
  seller_order_number: string,
  status: "Активная" | "Завершенная",
  total_amount: number,
  total_amount_excl_vat?: number,
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
  total_amount_excl_vat?: number,
  created_at: string,
  updated_at: string,
  buyer_name: string,
  buyer_inn: string,
  buyer_phone: string 
}

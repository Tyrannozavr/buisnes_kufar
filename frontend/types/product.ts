export interface Product {
  id: number
  company_id: number
  name: string
  description?: string
  article: string
  type: 'Товар' | 'Услуга'
  price: number
  images: string[]
  characteristics: Array<{
    name: string
    value: string
  }>
  is_hidden: boolean
  is_deleted: boolean
  slug: string
  unit_of_measurement?: string
  created_at: string
  updated_at: string
}

export interface ProductResponse {
  id: number
  company_id: number
  name: string
  description?: string
  article: string
  type: 'Товар' | 'Услуга'
  price: number
  images: string[]
  characteristics: Array<{
    name: string
    value: string
  }>
  is_hidden: boolean
  is_deleted: boolean
  slug: string
  unit_of_measurement?: string
  created_at: string
  updated_at: string
}

export interface ProductListResponse {
  products: ProductResponse[]
  total: number
  page: number
  per_page: number
}

export interface ProductItemPublic {
  name: string
  logo_url: string | null
  slug: string
  description: string
  article: string
  type: string
  price: number
  unit_of_measurement: string
	company_id: number
	company_name: string
}

export interface ProductPaginatedPublicResponse {
  products: ProductItemPublic[]
  total: number
  page: number
  per_page: number
}

// Новый тип для каталога
export interface ProductListPublicResponse {
  products: ProductItemPublic[]
  total: number
  page: number
  per_page: number
}

//интерфесы для страницы подтверждения
export interface ProductInCheckout  {
	slug: string
	type: string
	position: number
	productName: string
	article: number
	quantity: number
	units: string
	price: number
	amount:number
	description: string
	logoUrl: string
}

export interface CompaniesAndProducts  {
	companyId: number
	companyName: string
	products: ProductInCheckout[]
	services: ProductInCheckout[]
}

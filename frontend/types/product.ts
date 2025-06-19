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
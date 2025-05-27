export interface Product {
  id: string
  companyId: string
  name: string
  description: string
  article: string
  type: 'Товар' | 'Услуга'
  price: number
  images: string[]
  characteristics: Array<{
    name: string
    value: string
  }>
  isHidden: boolean
  isDeleted: boolean
  slug: string
}

export interface ProductResponse {
  data: Product[]
  pagination: {
    total: number
    page: number
    perPage: number
    totalPages: number
  }
} 
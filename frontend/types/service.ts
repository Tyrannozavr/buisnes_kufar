export interface Service {
  id: string
  companyId: string
  name: string
  description: string
  article: string
  type: 'Услуга'
  price: number
  images: string[]
  characteristics: Array<{
    name: string
    value: string
  }>
  isHidden: boolean
  isDeleted: boolean
}

export interface ServiceResponse {
  data: Service[]
  pagination: {
    total: number
    page: number
    perPage: number
    totalPages: number
  }
} 
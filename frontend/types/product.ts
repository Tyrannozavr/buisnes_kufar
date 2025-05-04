export interface Product {
  id: string
  companyId: string
  name: string
  type: string
  price: number
  images: string[]
  characteristics: { name: string; value: string }[]
  isHidden: boolean
  isDeleted: boolean
} 
export interface Review {
  id: string
  companyId: string
  userId: string
  authorName: string
  rating: number
  text: string
  date: string
  images?: string[]
} 
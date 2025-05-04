export interface Announcement {
  id: string
  companyId: string
  title: string
  content: string
  images: string[]
  createdAt: string
  isPublished: boolean
  notifyPartners: boolean
  notifySuppliers: boolean
  notifyBuyers: boolean
} 
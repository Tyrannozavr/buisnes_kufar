export interface Company {
  id: string
  name: string
  logo: string
  type: string
  activity: string
  description: string
  country: string
  region: string
  city: string
  fullName: string
  inn: string
  ogrn: string
  kpp: string
  registrationDate: string
  legalAddress: string
  productionAddress: string
  phone: string
  email: string
  website: string
}

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

export interface Message {
  id: string
  fromCompanyId: string
  toCompanyId: string
  subject: string
  content: string
  createdAt: string
  isRead: boolean
}

export interface Deal {
  id: string
  buyerId: string
  sellerId: string
  productId: string
  status: string
  createdAt: string
}
export interface FilterItem {
  label: string
  value: string
  count: number
}

export interface BaseSearchParams {
  search: string
  country: string
  federalDistrict: string
  region: string
  city: string
  minPrice?: number
  maxPrice?: number
}

export interface ProductSearchParams extends BaseSearchParams {
  inStock?: boolean
}

export interface ServiceSearchParams extends BaseSearchParams {
  inStock?: boolean
}

export interface ProductType {
  label: string
  value: 'construction' | 'tools' | 'equipment' | 'consumables' | 'plumbing' | 'electrical' | 'finishing' | 'other'
}

export interface ServiceType {
  label: string
  value: 'construction' | 'repair' | 'installation' | 'finishing' | 'design' | 'consultation' | 'other'
}

export interface ExperienceLevel {
  label: string
  value: 'less_than_1' | '1_to_3' | '3_to_5' | 'more_than_5'
}

export interface LocationItem {
  label: string
  value: string
}

export interface Pagination {
  currentPage: number
  totalPages: number
  totalItems: number
  itemsPerPage: number
}

export interface ProductResponse {
  data: Product[]
  pagination: Pagination
}

export interface ServiceResponse {
  data: Service[]
  pagination: Pagination
}

export interface Product {
  id: string
  name: string
  type: string
  price: number
  inStock: boolean
  country: string
  region: string
  city: string
  description: string
  images: string[]
}

export interface Service {
  id: string
  name: string
  type: string
  price: number
  inStock: boolean
  country: string
  region: string
  city: string
  description: string
  images: string[]
}

export type ViewMode = 'basic' | 'advanced'

// Type guards
export function isProductType(value: any): value is ProductType {
  return value && typeof value === 'object' && 'value' in value && 'label' in value
}

export function isServiceType(value: any): value is ServiceType {
  return value && typeof value === 'object' && 'value' in value && 'label' in value
}

export function isExperienceLevel(value: any): value is ExperienceLevel {
  return value && typeof value === 'object' && 'value' in value && 'label' in value
}

export function isLocationItem(value: any): value is LocationItem {
  return value && typeof value === 'object' && 'value' in value && 'label' in value
} 
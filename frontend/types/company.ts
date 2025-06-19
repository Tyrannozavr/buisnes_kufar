import type { LocationItem } from './location'

export type TradeActivity = 'Покупатель' | 'Продавец' | 'Покупатель и продавец'
export type BusinessType = 'Производство товаров' | 'Оказание услуг' | 'Производство товаров и оказание услуг'

export interface Company {
  id: number
  name: string
  logo_url: string | null
  type: string
  slug: string
  tradeActivity: TradeActivity
  businessType: BusinessType
  activityType: string
  description: string | null
  country: string
  federalDistrict: string
  region: string
  city: string
  fullName: string
  inn: string
  ogrn: string
  kpp: string
  registrationDate: string
  legalAddress: string
  productionAddress: string | null
  phone: string
  email: string
  website: string | null
  officials: CompanyOfficial[]
  totalViews: number
  monthlyViews: number
  totalPurchases: number
  createdAt: string
  updatedAt: string
}

// Base type for company officials
export interface CompanyOfficialBase {
  position: string
  full_name: string
}

// Extended type for company officials with additional properties
export interface CompanyOfficial extends CompanyOfficialBase {
  id: number
  company_id: number
}

// Type for partner company with only the required fields
export interface PartnerCompany {
  fullName: string
  slug: string
  logo: string | null
  businessType: string
  country: string
  region: string
  city: string
}

export interface CompanyDetails {
  id: number
  logo_url: string | null
  description: string
  inn: string
  ogrn: string
  ogrnDate: string
  kpp: string
  legalAddress: string
  productionAddress: string
  registrationDate: string
  phone: string
  email: string
  website: string
}

export interface CompanyStatistics {
  totalProducts: number
  totalViews: number
  monthlyViews: number
  registrationDate: string
  totalPurchases?: number
}

export interface ManufacturersSearchParams {
  search?: string
  country?: string
  federalDistrict?: string
  region?: string
  city?: string
  product?: string
}

// Define a simple manufacturer type
export interface CompanyShort {
  id: string
  logo: string | null
  name: string
  country: string
  region: string
  city: string
  description: string
  tradeActivity: string
}

export interface CompanyInfo {
  companyName: string
  companyLogo: string
}

export interface CompanyFormState {
    name: string
    inn: string
    kpp: string
    ogrn: string
    registrationDate: string
    legalAddress: string
    productionAddress: string
    country: LocationItem | undefined
    federalDistrict: LocationItem | undefined
    region: LocationItem | undefined
    city: LocationItem | undefined
    countryOptions: LocationItem[]
    federalDistrictOptions: LocationItem[]
    regionOptions: LocationItem[]
    cityOptions: LocationItem[]
}

export interface CompanyFormProps {
    modelValue: CompanyFormState
    loading?: boolean
    error?: string | null
}

export interface CompanyResponse {
  id: number
  name: string
  full_name: string
  logo: string | null
  logo_url: string | null
  type: string
  slug: string
  trade_activity: TradeActivity
  business_type: BusinessType
  activity_type: string
  description: string | null
  country: string
  federal_district: string
  region: string
  city: string
  inn: string
  ogrn: string
  kpp: string
  registration_date: string
  legal_address: string
  production_address: string | null
  phone: string
  email: string
  website: string | null
  officials: CompanyOfficial[]
  total_views: number
  monthly_views: number
  total_purchases: number
  created_at: string
  updated_at: string
}

export interface CompanyDataFormState {
  name: string
  fullName: string
  inn: string
  kpp: string
  ogrn: string
  registrationDate: string
  type: string
  tradeActivity: TradeActivity
  businessType: BusinessType
  activityType: string | null
  description: string | null
  website: string | null
  legalAddress: string | null
  phone: string | null
  email: string | null
  productionAddress: string | null
  country?: LocationItem
  federalDistrict?: LocationItem
  region?: LocationItem
  city?: LocationItem
  officials: CompanyOfficial[]
  logo: string | null
  logo_url: string | null
}

export interface CompanyDataFormProps {
  company?: CompanyResponse
  loading?: boolean
  isNewCompany?: boolean
}

export interface CompanyUpdate {
  name?: string
  full_name?: string
  inn?: string
  kpp?: string
  ogrn?: string
  registration_date?: string
  type?: string
  trade_activity?: TradeActivity
  business_type?: BusinessType
  activity_type?: string | null
  description?: string | null
  website?: string | null
  legal_address?: string | null
  phone?: string | null
  email?: string | null
  production_address?: string | null
  country?: string
  federal_district?: string
  region?: string
  city?: string
  officials?: CompanyOfficial[]
}

export interface CompanyProfile {
  id: number | null
  name: string | null
  logo: string | null
  email: string
  inn: string
  position: string | null
  isCompanyCreated: boolean
}

// Функция для формирования полного URL изображения
export const getFullImageUrl = (path: string | null): string | null => {
  if (!path) return null
  
  const config = useRuntimeConfig()
  const frontendUrl = config.public.frontendUrl || ''
  
  // Если путь уже полный URL, возвращаем как есть
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  
  // Убираем начальный слеш, если он есть
  const cleanPath = path.startsWith('/') ? path.slice(1) : path
  
  // Формируем полный URL
  return `${frontendUrl}/${cleanPath}`
}

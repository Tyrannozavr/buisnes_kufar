import type { Product, ProductResponse, ProductListResponse } from '~/types/product'
import { useNuxtApp } from 'nuxt/app'

// Типы для создания и обновления продуктов
export interface ProductCreate {
  name: string
  description?: string
  article: string
  type: 'Товар' | 'Услуга'
  price: number
  unit_of_measurement?: string
  is_hidden?: boolean
  images?: string[]
  characteristics?: Array<{
    name: string
    value: string
  }>
}

export interface ProductUpdate {
  name?: string
  description?: string
  article?: string
  type?: 'Товар' | 'Услуга'
  price?: number
  unit_of_measurement?: string
  is_hidden?: boolean
  images?: string[]
  characteristics?: Array<{
    name: string
    value: string
  }>
}

// URL-адреса API
const API_URLS = {
  BASE: '/v1/me/products',
  BY_ID: (id: number) => `/v1/me/products/${id}`,
  BY_SLUG: (slug: string) => `/v1/me/products/slug/${slug}`,
  BY_TYPE: (type: string) => `/v1/me/products/type/${type}`,
  TOGGLE_HIDDEN: (id: number) => `/v1/me/products/${id}`,
  IMAGES: (id: number) => `/v1/me/products/${id}/images`,
  RESTORE: (id: number) => `/v1/me/products/${id}`,
  HIDE: (id: number) => `/v1/me/products/${id}`,
  SHOW: (id: number) => `/v1/me/products/${id}/show`,
  HARD_DELETE: (id: number) => `/v1/me/products/${id}/hard`,
}

// Получить все продукты владельца компании
export const getMyProducts = async (params?: {
  skip?: number
  limit?: number
  include_hidden?: boolean
  include_deleted?: boolean
}): Promise<ProductListResponse> => {
  const { $api } = useNuxtApp()
  const searchParams = new URLSearchParams()
  
  if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
  if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
  if (params?.include_hidden !== undefined) searchParams.append('include_hidden', params.include_hidden.toString())
  if (params?.include_deleted !== undefined) searchParams.append('include_deleted', params.include_deleted.toString())
  
  const query = searchParams.toString()
  const url = `${API_URLS.BASE}${query ? `?${query}` : ''}`
  
  return await $api.get(url)
}

// Получить продукт по ID (только владелец)
export const getMyProduct = async (productId: number): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.get(API_URLS.BY_ID(productId))
}

// Получить продукт по slug (только владелец)
export const getMyProductBySlug = async (slug: string): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.get(API_URLS.BY_SLUG(slug))
}

// Получить продукты по типу (только владелец)
export const getMyProductsByType = async (type: 'Товар' | 'Услуга', params?: {
  skip?: number
  limit?: number
}): Promise<ProductListResponse> => {
  const { $api } = useNuxtApp()
  const searchParams = new URLSearchParams()
  
  if (params?.skip !== undefined) searchParams.append('skip', params.skip.toString())
  if (params?.limit !== undefined) searchParams.append('limit', params.limit.toString())
  
  const query = searchParams.toString()
  const url = `${API_URLS.BY_TYPE(type)}${query ? `?${query}` : ''}`
  
  return await $api.get(url)
}

// Создать новый продукт
export const createProduct = async (productData: ProductCreate): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.post(API_URLS.BASE, productData)
}

// Обновить продукт
export const updateProduct = async (productId: number, productData: ProductUpdate): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.put(API_URLS.BY_ID(productId), productData)
}

// Удалить продукт (мягкое удаление)
export const deleteProduct = async (productId: number): Promise<{ message: string }> => {
  const { $api } = useNuxtApp()
  return await $api.delete(API_URLS.BY_ID(productId))
}

// Полное удаление продукта
export const hardDeleteProduct = async (productId: number): Promise<{ message: string }> => {
  const { $api } = useNuxtApp()
  return await $api.delete(API_URLS.HARD_DELETE(productId))
}

// Переключить видимость продукта
export const toggleProductHidden = async (productId: number): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.put(API_URLS.TOGGLE_HIDDEN(productId))
}

// Обновить изображения продукта
export const updateProductImages = async (productId: number, images: string[]): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.put(API_URLS.IMAGES(productId), { images })
}

// Восстановить продукт (из удаленных)
export const restoreProduct = async (productId: number): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.patch(API_URLS.RESTORE(productId), {is_deleted: false, is_hidden: false})
}

// Скрыть продукт
export const hideProduct = async (productId: number): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.patch(API_URLS.HIDE(productId), {is_hidden: true})
}

// Показать продукт
export const showProduct = async (productId: number): Promise<ProductResponse> => {
  const { $api } = useNuxtApp()
  return await $api.put(API_URLS.SHOW(productId))
}
import { defineEventHandler } from 'h3'
import type { Product } from '~/types/product'

// Mock data for products
const products: Product[] = [
  {
    id: '1',
    companyId: '1',
    name: 'Промышленный станок ЧПУ',
    type: 'product',
    price: 1500000,
    images: ['/images/products/cnc-machine-1.jpg', '/images/products/cnc-machine-2.jpg'],
    characteristics: [
      { name: 'Мощность', value: '5 кВт' },
      { name: 'Рабочая зона', value: '1000x1000x500 мм' },
      { name: 'Точность', value: '0.01 мм' }
    ],
    isHidden: false,
    isDeleted: false
  },
  {
    id: '2',
    companyId: '2',
    name: 'Строительство коттеджа',
    type: 'service',
    price: 5000000,
    images: ['/images/services/cottage-1.jpg', '/images/services/cottage-2.jpg'],
    characteristics: [
      { name: 'Площадь', value: '150 м²' },
      { name: 'Сроки', value: '6 месяцев' },
      { name: 'Гарантия', value: '5 лет' }
    ],
    isHidden: false,
    isDeleted: false
  },
  {
    id: '3',
    companyId: '3',
    name: 'Система автоматизации производства',
    type: 'product',
    price: 2500000,
    images: ['/images/products/automation-system-1.jpg', '/images/products/automation-system-2.jpg'],
    characteristics: [
      { name: 'Тип', value: 'Модульная' },
      { name: 'Совместимость', value: 'Универсальная' },
      { name: 'Гарантия', value: '3 года' }
    ],
    isHidden: false,
    isDeleted: false
  }
]

export default defineEventHandler(async (event) => {
  // TODO: Implement proper authentication
  // For now, we'll just return mock data
  return products
})
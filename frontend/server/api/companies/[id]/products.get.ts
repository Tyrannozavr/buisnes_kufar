import type { Product } from '~/types/product'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // Sample products data
  const products: Product[] = [
    {
      id: '1',
      companyId: id,
      name: 'Токарный станок ТС-2000',
      description: 'Современный токарный станок с ЧПУ для обработки металлических деталей',
      price: 1500000,
      images: ['/images/products/ts-2000-1.jpg', '/images/products/ts-2000-2.jpg'],
      category: 'Станки',
      specifications: {
        dimensions: '2000x1500x1800 мм',
        weight: '2500 кг',
        power: '15 кВт'
      }
    },
    {
      id: '2',
      companyId: id,
      name: 'Фрезерный станок ФС-1500',
      description: 'Универсальный фрезерный станок для обработки различных материалов',
      price: 2000000,
      images: ['/images/products/fs-1500-1.jpg', '/images/products/fs-1500-2.jpg'],
      category: 'Станки',
      specifications: {
        dimensions: '1800x1400x1600 мм',
        weight: '2200 кг',
        power: '12 кВт'
      }
    }
  ]

  return products
}) 
import { defineEventHandler, getQuery } from 'h3'
import type { Product } from '~/types/product'

// Mock data for products
const products: Product[] = [
  {
    id: '4',
    companyId: '1',
    name: 'Промышленный станок ЧПУ',
    description: 'Высокоточный промышленный станок с числовым программным управлением для обработки металла. Подходит для серийного производства деталей сложной формы.',
    article: 'CNC-5000',
    type: 'Товар',
    price: 1500000,
    images: [
      'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
    ],
    characteristics: [
      { name: 'Мощность', value: '5 кВт' },
      { name: 'Рабочая зона', value: '1000x1000x500 мм' },
      { name: 'Точность', value: '0.01 мм' }
    ],
    isHidden: false,
    isDeleted: false,
    slug: 'promyshlennyj-stanok-chpu'
  },
  {
    id: '5',
    companyId: '2',
    name: 'Строительство коттеджа',
    description: 'Полный комплекс услуг по строительству коттеджа под ключ. Включает проектирование, закупку материалов, строительные работы и финишную отделку.',
    article: 'HOUSE-150',
    type: 'Услуга',
    price: 5000000,
    images: [
      'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
    ],
    characteristics: [
      { name: 'Площадь', value: '150 м²' },
      { name: 'Сроки', value: '6 месяцев' },
      { name: 'Гарантия', value: '5 лет' }
    ],
    isHidden: false,
    isDeleted: false,
    slug: 'stroitelstvo-kottedzha'
  },
  {
    id: '6',
    companyId: '3',
    name: 'Система автоматизации производства',
    description: 'Комплексное решение для автоматизации производственных процессов. Включает программное обеспечение, датчики и контроллеры для оптимизации работы предприятия.',
    article: 'AUTO-2500',
    type: 'Товар',
    price: 2500000,
    images: [
      'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
    ],
    characteristics: [
      { name: 'Тип', value: 'Модульная' },
      { name: 'Совместимость', value: 'Универсальная' },
      { name: 'Гарантия', value: '3 года' }
    ],
    isHidden: false,
    isDeleted: false,
    slug: 'sistema-avtomatizacii-proizvodstva'
  },
  {
    id: '7',
    companyId: '3',
    name: 'Система автоматизации производства',
    description: 'Комплексное решение для автоматизации производственных процессов. Включает программное обеспечение, датчики и контроллеры для оптимизации работы предприятия.',
    article: 'AUTO-2500',
    type: 'Товар',
    price: 2500000,
    images: [],
    characteristics: [
      { name: 'Тип', value: 'Модульная' },
      { name: 'Совместимость', value: 'Универсальная' },
      { name: 'Гарантия', value: '3 года' }
    ],
    isHidden: true,
    isDeleted: false,
    slug: 'sistema-avtomatizacii-proizvodstva-2'
  },
  {
    id: '8',
    companyId: '3',
    name: 'Система автоматизации производства',
    description: 'Комплексное решение для автоматизации производственных процессов. Включает программное обеспечение, датчики и контроллеры для оптимизации работы предприятия.',
    article: 'AUTO-2500',
    type: 'Товар',
    price: 2500000,
    images: ['https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'],
    characteristics: [
      { name: 'Тип', value: 'Модульная' },
      { name: 'Совместимость', value: 'Универсальная' },
      { name: 'Гарантия', value: '3 года' }
    ],
    isHidden: false,
    isDeleted: true,
    slug: 'sistema-avtomatizacii-proizvodstva-3'
  },
]

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const page = parseInt(query.page as string) || 1
  const perPage = parseInt(query.perPage as string) || 10
  const limit = parseInt(query.limit as string)

  // Filter out hidden and deleted products
  // const filteredProducts = products.filter(p => !p.isHidden && !p.isDeleted)
  const filteredProducts = products

  // Apply limit if specified
  const limitedProducts = limit ? filteredProducts.slice(0, limit) : filteredProducts

  // Calculate pagination
  const startIndex = (page - 1) * perPage
  const endIndex = startIndex + perPage
  const paginatedProducts = limitedProducts.slice(startIndex, endIndex)

  return {
    data: paginatedProducts,
    pagination: {
      total: limitedProducts.length,
      page,
      perPage,
      totalPages: Math.ceil(limitedProducts.length / perPage)
    }
  }
})
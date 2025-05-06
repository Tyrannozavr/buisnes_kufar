import { defineEventHandler } from 'h3'
import type { Product } from '~/types/product'

// Mock data for products
const products: Product[] = [
  {
    id: '1',
    companyId: '1',
    name: 'Промышленный станок ЧПУ',
    type: 'продукт',
    price: 1500000,
    images: ['https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'],
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
    type: 'услуга',
    price: 5000000,
    images: ['https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'],
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
    type: 'продукт',
    price: 2500000,
    images: ['https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
      'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'],
    characteristics: [
      { name: 'Тип', value: 'Модульная' },
      { name: 'Совместимость', value: 'Универсальная' },
      { name: 'Гарантия', value: '3 года' }
    ],
    isHidden: false,
    isDeleted: false
  }
]

export default defineEventHandler(async (_event) => {
  // TODO: Implement proper authentication
  // For now, we'll just return mock data
  return products
})
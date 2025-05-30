import { defineEventHandler } from 'h3'
import type { Product } from '~/types/product'

// Mock data for products
const products: Product[] = [
  {
    id: '1',
    companyId: '1',
    name: 'Промышленный станок ЧПУ',
    slug: 'promyshlennyj-stanok-chpu',
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
    isDeleted: false
  },
  {
    id: '2',
    companyId: '2',
    name: 'Строительство коттеджа',
    slug: 'stroitelstvo-kottedzha',
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
    isDeleted: false
  },
  {
    id: '3',
    companyId: '3',
    name: 'Система автоматизации производства',
    slug: 'sistema-avtomatizacii-proizvodstva',
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
    isDeleted: false
  }
]

export default defineEventHandler(async (event) => {
  const id = event.context.params?.id

  // Default product data
  const defaultProduct: Product = {
    id: id || 'default',
    companyId: 'default',
    name: 'Стандартный продукт',
    slug: 'standartnyj-produkt',
    description: 'Это стандартное описание продукта, возвращаемое по умолчанию.',
    article: 'STD-1000',
    type: 'Товар',
    price: 100000,
    images: [
      'https://www.shareicon.net/data/2016/02/27/725765_commerce_512x512.png',
      'https://cdn2.iconfinder.com/data/icons/media-advertising-2/64/monitor-ecommerce-screen-multimedia-broswer-online_shop-shopping_cart-online_shopping-1024.png'
    ],
    characteristics: [
      { name: 'Характеристика 1', value: 'Значение 1' },
      { name: 'Характеристика 2', value: 'Значение 2' },
      { name: 'Характеристика 3', value: 'Значение 3' }
    ],
    isHidden: false,
    isDeleted: false
  }

  return defaultProduct
})
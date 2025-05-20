import type { Product } from '~/types/product'

export default defineEventHandler(async (event) => {
  // TODO: Implement proper authentication and database query
  // For now, return mock data
  const products: Product[] = [
    {
      id: '1',
      companyId: '1',
      name: 'Токарный станок ТС-2000',
      description: 'Современный токарный станок с ЧПУ для обработки металлических деталей',
      article: 'TS-2000',
      type: 'Товар',
      price: 1500000,
      images: [
        'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
        'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
      ],
      characteristics: [
        { name: 'Мощность', value: '15 кВт' },
        { name: 'Рабочая зона', value: '2000x1500x1800 мм' },
        { name: 'Вес', value: '2500 кг' }
      ],
      isHidden: false,
      isDeleted: false
    },
    {
      id: '2',
      companyId: '1',
      name: 'Фрезерный станок ФС-1500',
      description: 'Универсальный фрезерный станок для обработки различных материалов',
      article: 'FS-1500',
      type: 'Товар',
      price: 2000000,
      images: [
        'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album',
        'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13'
      ],
      characteristics: [
        { name: 'Мощность', value: '12 кВт' },
        { name: 'Рабочая зона', value: '1800x1400x1600 мм' },
        { name: 'Вес', value: '2200 кг' }
      ],
      isHidden: false,
      isDeleted: false
    }
  ]

  return products
}) 
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
      images: [
        'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13',
        'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album'
      ],
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
      images: [
        'https://sun9-46.userapi.com/impg/F9XKPxJqTPezmGGqDxcq18fg2pOgtjN-Z3Mw3A/kVsdXio6eiY.jpg?size=1024x1024&quality=95&sign=8b4c9f42d446b73f8750b994fba07c04&c_uniq_tag=joEYHEddID5Gt57ZiK5Y46vnerjvYPvp993bnAOYW_Q&type=album',
        'https://avatars.mds.yandex.net/i?id=e3da028f7e2306302e561bdea6d5b5794595bc8bc9dd0653-5189723-images-thumbs&n=13'
      ],
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
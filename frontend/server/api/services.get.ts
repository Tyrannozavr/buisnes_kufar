import { defineEventHandler } from 'h3'
import type { Product } from '~/types/product'

// Mock data for services
const services: Product[] = [
  {
    id: '1',
    companyId: '1',
    name: 'Консультация по автоматизации',
    description: 'Профессиональная консультация по внедрению систем автоматизации на предприятии.',
    article: 'CONSULT-100',
    type: 'Услуга',
    price: 100000,
    images: ['https://www.rndbur.ru/images/profosmotr/Трудоустройство.png'],
    characteristics: [
      { name: 'Длительность', value: '2 часа' },
      { name: 'Формат', value: 'Онлайн' },
      { name: 'Гарантия', value: '1 месяц' }
    ],
    isHidden: false,
    isDeleted: false
  },
  {
    id: '2',
    companyId: '2',
    name: 'Обучение персонала',
    description: 'Комплексное обучение сотрудников работе с новыми системами автоматизации.',
    article: 'TRAIN-200',
    type: 'Услуга',
    price: 300000,
    images: ['https://med-jur-help.ru/upload/uf/f81/0kgvw3gh2vr93yntlo1u2lddk54lxprs/classroom.svg'],
    characteristics: [
      { name: 'Длительность', value: '5 дней' },
      { name: 'Формат', value: 'Очный' },
      { name: 'Гарантия', value: '6 месяцев' }
    ],
    isHidden: false,
    isDeleted: false
  },
  {
    id: '3',
    companyId: '3',
    name: 'Аудит производственных процессов',
    description: 'Анализ и оптимизация текущих производственных процессов для повышения эффективности.',
    article: 'AUDIT-300',
    type: 'Услуга',
    price: 500000,
    images: ['https://admbaraba.nso.ru/sites/admbaraba.nso.ru/wodby_files/files/news/2023/02/ohrana.jpg'],
    characteristics: [
      { name: 'Длительность', value: '1 месяц' },
      { name: 'Формат', value: 'Смешанный' },
      { name: 'Гарантия', value: '1 год' }
    ],
    isHidden: false,
    isDeleted: false
  }
]

export default defineEventHandler(async (_event) => {
  // TODO: Implement proper authentication
  // For now, we'll just return mock data
  return services
})
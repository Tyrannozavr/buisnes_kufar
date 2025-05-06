import { defineEventHandler } from 'h3'
import type { Category } from '~/types/category'

export const categories: Category[] = [
  {
    id: '1',
    name: 'Товары',
    description: 'Объявления о товарах и продукции компании'
  },
  {
    id: '2',
    name: 'Услуги',
    description: 'Объявления об услугах, предоставляемых компанией'
  },
  {
    id: '3',
    name: 'Акции',
    description: 'Специальные предложения, скидки и акции'
  },
  {
    id: '4',
    name: 'Партнерство',
    description: 'Предложения о сотрудничестве и партнерстве'
  },
  {
    id: '5',
    name: 'События',
    description: 'Информация о мероприятиях, выставках и конференциях'
  },
  {
    id: '6',
    name: 'Вакансии',
    description: 'Объявления о вакансиях и наборе персонала'
  },
  {
    id: '7',
    name: 'Новости',
    description: 'Новости компании и отрасли'
  }
]

export default defineEventHandler(async (event) => {
  // Simulate a delay to show loading state
  await new Promise(resolve => setTimeout(resolve, 300))
  
  return categories
})
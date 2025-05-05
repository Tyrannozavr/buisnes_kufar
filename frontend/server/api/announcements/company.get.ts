import { defineEventHandler } from 'h3'
import type { Announcement } from '~/types/announcement'

export default defineEventHandler(async (event) => {
  // In a real application, you would:
  // 1. Get the authenticated user/company from the session
  // 2. Query your database for announcements belonging to that company
  // 3. Return the results

  // For now, we'll return mock data
  const mockAnnouncements: Announcement[] = [
    {
      id: '1',
      title: 'Новая линейка продукции',
      content: 'Наша компания запускает новую линейку экологически чистых продуктов.',
      status: 'published',
      createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
      companyId: '1',
      category: 'product',
      images: []
    },
    {
      id: '2',
      title: 'Скидки на оптовые заказы',
      content: 'Предлагаем специальные условия для оптовых клиентов. Скидки до 25% при заказе от 100 единиц товара.',
      status: 'draft',
      createdAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      companyId: '1',
      category: 'promotion',
      images: []
    },
    {
      id: '3',
      title: 'Ищем дистрибьюторов',
      content: 'В связи с расширением бизнеса, ищем партнеров для дистрибуции нашей продукции в регионах.',
      status: 'published',
      createdAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
      companyId: '1',
      category: 'partnership',
      images: []
    }
  ]

  // Simulate a delay to show loading state
  await new Promise(resolve => setTimeout(resolve, 500))

  return mockAnnouncements
})
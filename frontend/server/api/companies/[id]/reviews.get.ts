import type { Review } from '~/types/review'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // Sample reviews data
  const reviews: Review[] = [
    {
      id: '1',
      companyId: id,
      userId: 'user1',
      userName: 'Иван Петров',
      rating: 5,
      text: 'Отличное качество продукции и сервиса. Рекомендую!',
      date: '2024-03-15',
      images: ['/images/reviews/review1-1.jpg']
    },
    {
      id: '2',
      companyId: id,
      userId: 'user2',
      userName: 'Анна Сидорова',
      rating: 4,
      text: 'Хорошая компания, но есть куда расти в плане сервиса.',
      date: '2024-03-10',
      images: []
    }
  ]

  return reviews
}) 
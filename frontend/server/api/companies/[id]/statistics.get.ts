import type { CompanyStatistics } from '~/types/company'

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  
  // Sample statistics data
  const statistics: CompanyStatistics = {
    totalProducts: 15,
    totalViews: 1234,
    monthlyViews: 123,
    registrationDate: '12.05.2023',
    totalPurchases: 0
  }

  return statistics
})
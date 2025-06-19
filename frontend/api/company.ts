import type { CompanyResponse, CompanyStatistics } from '~/types/company'

export const getCompanyStatistics = async (id: string): Promise<{ data: CompanyStatistics }> => {
  // В реальном приложении здесь был бы API-запрос
  return {
    data: {
      totalViews: 0,
      monthlyViews: 0,
      totalPurchases: 0,
      // Добавьте другие статистические поля, если они есть в CompanyStatisticsResponse
    }
  }
}

export const getCompanyProducts = async (id: string): Promise<{ data: CompanyStatistics }> => {
  // В реальном приложении здесь был бы API-запрос
  return {
    data: [] // Пустой массив продуктов
  }
}

export const getCompany = async (id: string): Promise<{ data: CompanyResponse }> => {
  // В реальном приложении здесь был бы API-запрос
  return {
    data: {
      id: id,
      name: '',
      description: '',
      inn: '',
      ogrn: '',
      registrationDate: '',
      kpp: '',
      legalAddress: '',
      productionAddress: '',
      phone: '',
      email: '',
      website: '',
      logo: null,
      // Добавьте другие поля, которые могут быть в CompanyResponse
    }
  }
}
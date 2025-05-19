import { defineEventHandler } from 'h3'
import type { NewsItem } from '~/types/news'
import { companies } from './companies.get'

export default defineEventHandler(() => {
  // Convert companies to news items
  const news: NewsItem[] = companies.map(company => ({
    id: company.id.toString(),
    title: `Новая компания "${company.name}" присоединилась к платформе`,
    content: `${company.name} - ${company.activityType}. ${company.description}`,
    date: company.registrationDate,
    companySlug: company.slug,
    companyLogo: company.logo,
    activityType: company.activityType
  }))

  // Sort by registration date (newest first)
  return news.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})
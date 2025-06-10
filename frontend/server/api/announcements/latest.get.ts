import { defineEventHandler, getQuery } from 'h3'
import type { Announcement } from '~/types/announcement'
import { announcements } from './company.get'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const limit = Number(query.limit) || 6

  // Get latest announcements and transform to required format
  const data = announcements
    .slice(0, limit)
    .map(announcement => ({
      id: announcement.id,
      companyId: announcement.companyId,
      companyName: announcement.companyName,
      companyLogo: announcement.companyLogo,
      title: announcement.title,
      content: announcement.content,
      images: announcement.images,
      createdAt: announcement.createdAt,
      updatedAt: announcement.updatedAt,
      date: announcement.date,
      topic: announcement.topic,
      category: announcement.category,
      published: announcement.published,
      notifications: announcement.notifications
    } as Announcement))

  return {
    data,
    pagination: {
      total: announcements.length,
      page: 1,
      perPage: limit,
      totalPages: Math.ceil(announcements.length / limit)
    }
  }
}) 
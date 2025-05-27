import { defineEventHandler, getQuery } from 'h3'
import type { Announcement, AnnouncementCard } from '~/types/announcement'
import { announcements } from './company.get'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const page = Number(query.page) || 1
  const perPage = Number(query.perPage) || 10

  // Calculate pagination
  const total = announcements.length
  const totalPages = Math.ceil(total / perPage)
  const start = (page - 1) * perPage
  const end = start + perPage

  // Get paginated data and transform to AnnouncementCard format
  const data = announcements.slice(start, end).map(announcement => ({
    id: announcement.id,
    image: announcement.images[0] || announcement.image,
    title: announcement.title,
    date: announcement.date
  } as AnnouncementCard))

  return {
    data,
    pagination: {
      total,
      page,
      perPage,
      totalPages
    }
  }
}) 
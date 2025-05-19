import { defineEventHandler } from 'h3'
import { announcements } from './announcements/company.get'
// Mock data for announcements


export default defineEventHandler(async (event) => {
  // TODO: Implement proper authentication
  // For now, we'll just return mock data
  return announcements.map(announcement => ({
    id: announcement.id,
    image: announcement.images[0], // Take the first image
    title: announcement.title,
    date: announcement.createdAt
  }))
})
import { defineEventHandler } from 'h3'
import { announcements } from "~/server/api/announcements/company.get";

export default defineEventHandler((event) => {
  const id = event.context.params?.id

  // Mock data - in a real application, you would fetch this from a database

  // Find the announcement with the matching ID
  const announcement = announcements.find(a => a.id === id)

  // If no announcement is found, return a 404 error
  if (!announcement) {
    return {
      statusCode: 404,
      body: {
        message: `Announcement with ID ${id} not found`
      }
    }
  }

  // Return the announcement with required fields plus content
  return {
    id: announcement.id,
    image: announcement.images[0],
    title: announcement.title,
    date: announcement.createdAt,
    createdAt: announcement.createdAt,
    updatedAt: announcement.createdAt,
    content: announcement.content
  }
})
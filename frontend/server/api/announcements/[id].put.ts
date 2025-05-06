import { defineEventHandler, readBody } from 'h3'
import type { Announcement } from '~/types/announcement'

export default defineEventHandler(async (event) => {
  const id = event.context.params?.id
  const body = await readBody(event)

  // In a real application, you would update the announcement in a database
  // For this mock API, we'll just return a success response with the updated data

  // Validate required fields
  if (!body.title) {
    return {
      statusCode: 400,
      body: {
        message: 'Title is required'
      }
    }
  }

  if (!body.content) {
    return {
      statusCode: 400,
      body: {
        message: 'Content is required'
      }
    }
  }

  // Create updated announcement object
  const updatedAnnouncement: Partial<Announcement> = {
    ...body,
    id,
    updatedAt: new Date().toISOString()
  }

  // Return the updated announcement
  return {
    statusCode: 200,
    body: updatedAnnouncement
  }
})
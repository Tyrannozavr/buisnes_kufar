import { defineEventHandler, readMultipartFormData, createError } from 'h3'
import { mockMessages } from '~/server/mock/chatData'
import { writeFile } from 'node:fs/promises'
import { join } from 'node:path'

// Создаем директорию для файлов, если она не существует
const UPLOAD_DIR = join(process.cwd(), 'public', 'uploads')

export default defineEventHandler(async (event) => {
  const formData = await readMultipartFormData(event)
  if (!formData) {
    throw createError({
      statusCode: 400,
      message: 'Invalid form data'
    })
  }

  const chatId = formData.find(f => f.name === 'chatId')?.data.toString()
  const senderId = formData.find(f => f.name === 'senderId')?.data.toString()
  const content = formData.find(f => f.name === 'content')?.data.toString()
  const file = formData.find(f => f.name === 'file')

  if (!chatId || !senderId || (!content && !file)) {
    throw createError({
      statusCode: 400,
      message: 'Chat ID, sender ID and either content or file are required'
    })
  }

  let fileData = undefined
  if (file) {
    // Генерируем уникальное имя файла
    const timestamp = Date.now()
    const originalName = file.filename || 'file'
    const fileName = `${timestamp}-${originalName}`
    const filePath = join(UPLOAD_DIR, fileName)

    // Сохраняем файл
    await writeFile(filePath, file.data)

    fileData = {
      name: originalName,
      url: `/uploads/${fileName}`,
      type: file.type || 'application/octet-stream',
      size: file.data.length
    }
  }

  // Create new message
  const newMessage = {
    id: `msg${Date.now()}`,
    chatId,
    sender: {
      id: senderId,
      name: 'Current Company', // In real implementation, get from user data
      logo: '/images/default-company-logo.png'
    },
    content: content || '',
    file: fileData,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }

  // Add message to mock data
  if (!mockMessages[chatId]) {
    mockMessages[chatId] = []
  }
  mockMessages[chatId].push(newMessage)

  return newMessage
}) 
import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const { email, code } = await readBody(event)
  
  // Mock verification - in real app this would verify against stored code
  if (code === '123456') { // Mock code for testing
    return {
      success: true,
      message: 'Код подтвержден'
    }
  }
  
  return {
    success: false,
    message: 'Неверный код подтверждения'
  }
}) 
import { defineEventHandler, readBody } from 'h3'

export default defineEventHandler(async (event) => {
  const { oldPassword, newPassword } = await readBody(event)
  
  // Mock password change - in real app this would verify old password and update to new one
  if (oldPassword === 'oldpass123') { // Mock old password for testing
    return {
      success: true,
      message: 'Пароль успешно изменен'
    }
  }
  
  return {
    success: false,
    message: 'Неверный текущий пароль'
  }
}) 
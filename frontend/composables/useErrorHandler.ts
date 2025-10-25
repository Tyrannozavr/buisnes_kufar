import type { ApiError } from '~/types/auth'

export function useErrorHandler() {
  const toast = useToast()

  function handleApiError(error: any, context?: string) {
    console.error(`❌ ${context || 'API'} error:`, error)
    
    const apiError = error as ApiError
    
    // Обработка специфических ошибок ИНН
    if (apiError.detail?.includes('ИНН') && apiError.detail?.includes('уже используется')) {
      toast.add({
        title: 'Ошибка ИНН',
        description: apiError.detail,
        color: 'error',
        icon: 'i-heroicons-exclamation-triangle',
        timeout: 8000
      })
      return
    }
    
    // Обработка ошибок валидации полей
    if (apiError.errors) {
      Object.entries(apiError.errors).forEach(([field, messages]) => {
        const errorMessage = messages.join(', ')
        toast.add({
          title: `Ошибка в поле "${field}"`,
          description: errorMessage,
          color: 'error',
          icon: 'i-heroicons-exclamation-circle',
          timeout: 6000
        })
      })
      return
    }
    
    // Обработка общих ошибок
    const message = apiError.message || apiError.detail || 'Произошла ошибка'
    
    // Специфические сообщения для разных контекстов
    let title = 'Ошибка'
    if (context === 'profile') {
      title = 'Ошибка обновления профиля'
    } else if (context === 'registration') {
      title = 'Ошибка регистрации'
    } else if (context === 'login') {
      title = 'Ошибка входа'
    }
    
    toast.add({
      title,
      description: message,
      color: 'error',
      icon: 'i-heroicons-exclamation-circle',
      timeout: 5000
    })
  }

  function handleSuccess(message: string, context?: string) {
    let title = 'Успешно'
    if (context === 'profile') {
      title = 'Профиль обновлен'
    } else if (context === 'registration') {
      title = 'Регистрация завершена'
    }
    
    toast.add({
      title,
      description: message,
      color: 'success',
      icon: 'i-heroicons-check-circle',
      timeout: 3000
    })
  }

  return {
    handleApiError,
    handleSuccess
  }
}


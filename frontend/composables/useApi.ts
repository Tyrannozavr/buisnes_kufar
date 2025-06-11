import { useNuxtApp } from 'nuxt/app'
import type { UseFetchOptions } from 'nuxt/app'
import { ref } from 'vue'

interface ApiInstance {
  get: (url: string, params?: Record<string, any>) => Promise<any>
  post: (url: string, data?: Record<string, any>) => Promise<any>
  put: (url: string, data?: Record<string, any>) => Promise<any>
  delete: (url: string) => Promise<any>
  clearCache: () => void
}

export function useApi<T>(url: string, options: UseFetchOptions<T> = {}) {
  const { $api } = useNuxtApp()
  const api = $api as ApiInstance
  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const pending = ref(true)

  const fetchData = async () => {
    try {
      pending.value = true
      error.value = null
      
      const response = await api.get(url, {
        ...options,
        params: options.params || {}
      })
      data.value = response as T
    } catch (e) {
      error.value = e instanceof Error ? e : new Error('An error occurred')
    } finally {
      pending.value = false
    }
  }

  // If not lazy, fetch immediately
  if (!options.lazy) {
    fetchData()
  }

  return {
    data,
    error,
    pending,
    refresh: fetchData
  }
}
import type { UseFetchOptions } from 'nuxt/app'
import type { FetchOptions } from 'ofetch'

type HttpMethod = 'GET' | 'HEAD' | 'PATCH' | 'POST' | 'PUT' | 'DELETE' | 'CONNECT' | 'OPTIONS' | 'TRACE'

export function useApi<T>(url: string, options: UseFetchOptions<T> = {}) {
  const config = useRuntimeConfig()
  const apiBaseUrl = config.public.apiBaseUrl

  // Ensure URL starts with apiBaseUrl if it doesn't include http
  const apiUrl = url.startsWith('http') ? url : `${apiBaseUrl}${url.startsWith('/') ? '' : '/'}${url}`

  // For POST, PUT, DELETE requests, use $fetch directly
  if (options.method && ['POST', 'PUT', 'DELETE'].includes(options.method as string)) {
    const fetchOptions: FetchOptions = {
      method: (options.method as string).toUpperCase() as HttpMethod,
      body: options.body,
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> || {})
      }
    }
    return $fetch<T>(apiUrl, fetchOptions)
  }

  // For GET requests, use useFetch
  const defaults: UseFetchOptions<T> = {
    credentials: 'include',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    ...options
  }

  return useFetch<T>(apiUrl, defaults as never)
}
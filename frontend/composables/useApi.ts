import type { UseFetchOptions } from 'nuxt/app'

export function useApi<T>(url: string, options: UseFetchOptions<T> = {}) {
  // Ensure URL starts with /api if it doesn't include http
  const apiUrl = url.startsWith('http') ? url : url.startsWith('/api') ? url : `/api${url.startsWith('/') ? '' : '/'}${url}`

  // Set default options for all API requests
  const defaults: UseFetchOptions<T> = {
    // Enable cookie passing
    credentials: 'include',
    // Default headers
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    // Add any other default options here
    ...options
  }

  // Use Nuxt's built-in useFetch with our defaults
  return useFetch<T>(apiUrl, defaults as never)
}
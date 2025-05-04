import { defineNuxtPlugin, useRuntimeConfig } from '#app'
import type { FetchOptions } from 'ofetch';
import { $fetch } from 'ofetch'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl || 'http://localhost:8000/api'

  // Create a custom fetch instance with base configuration
  const apiFetch = $fetch.create({
    baseURL,
    credentials: 'include', // This ensures cookies are sent with requests
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  })

  // Create a cache for SSR requests to avoid duplicate requests
  const ssrCache = new Map()

  // Custom fetch function that handles SSR caching
  const fetchWithCache = async (url: string, options: FetchOptions = {}) => {
    const cacheKey = `${url}-${JSON.stringify(options)}`
    
    // If we're on the server and have a cached response, return it
    if (import.meta.server && ssrCache.has(cacheKey)) {
      return ssrCache.get(cacheKey)
    }
    
    try {
      const response = await apiFetch(url, options)
      
      // Cache the response if we're on the server
      if (import.meta.server) {
        ssrCache.set(cacheKey, response)
      }
      
      return response
    } catch (error) {
      console.error('API request error:', error)
      throw error
    }
  }

  // API methods
  const api = {
    // GET request
    get: (url: string, params = {}) => {
      return fetchWithCache(url, { method: 'GET', params })
    },
    
    // POST request (typically from client)
    post: (url: string, data = {}) => {
      return fetchWithCache(url, { method: 'POST', body: data })
    },
    
    // PUT request
    put: (url: string, data = {}) => {
      return fetchWithCache(url, { method: 'PUT', body: data })
    },
    
    // DELETE request
    delete: (url: string) => {
      return fetchWithCache(url, { method: 'DELETE' })
    },
    
    // Clear cache (useful for logout or other state changes)
    clearCache: () => {
      ssrCache.clear()
    }
  }

  // Make the API available throughout the app
  nuxtApp.provide('api', api)
})

// Type definitions for better TypeScript support
declare module '#app' {
  interface NuxtApp {
    $api: {
      get: (url: string, params?: Record<string, any>) => Promise<any>
      post: (url: string, data?: Record<string, any>) => Promise<any>
      put: (url: string, data?: Record<string, any>) => Promise<any>
      delete: (url: string) => Promise<any>
      clearCache: () => void
    }
  }
}
import { defineNuxtPlugin, useRuntimeConfig } from 'nuxt/app'
import type { FetchOptions } from 'ofetch'
import { $fetch } from 'ofetch'
import type { Plugin } from 'nuxt/app'
import { useCookie } from 'nuxt/app'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl || 'http://localhost:8000/api'
  const accessToken = useCookie('access_token')

  // Create a custom fetch instance with base configuration
  const apiFetch = $fetch.create({
    baseURL,
    credentials: 'include',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    // Add CORS mode
    mode: 'cors',
    // Add authorization header if token exists
    onRequest({ options }) {
      if (accessToken.value) {
        const headers = new Headers(options.headers as HeadersInit)
        headers.set('Authorization', `Bearer ${accessToken.value}`)
        options.headers = headers
      }
    },
    // Add global error handler
    onResponseError({ response }) {
      if (response.status === 401) {
        // Clear the access token
        accessToken.value = null
        // Redirect to login page
        navigateTo('/auth/login')
      }
    }
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
      // Merge options with base configuration
      const mergedOptions: FetchOptions = {
        ...options,
        credentials: 'include',
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          ...(options.headers || {})
        }
      }

      // Add authorization header if token exists
      if (accessToken.value) {
        const headers = new Headers(mergedOptions.headers as HeadersInit)
        headers.set('Authorization', `Bearer ${accessToken.value}`)
        mergedOptions.headers = headers
      }
      
      const response = await apiFetch(url, mergedOptions)
      
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
    get: (url: string, options: FetchOptions = {}) => {
      return fetchWithCache(url, { method: 'GET', ...options })
    },
    
    // POST request
    post: (url: string, data = {}, options: FetchOptions = {}) => {
      return fetchWithCache(url, { method: 'POST', body: data, ...options })
    },
    
    // PUT request
    put: (url: string, data = {}, options: FetchOptions = {}) => {
      return fetchWithCache(url, { method: 'PUT', body: data, ...options })
    },
    
    // DELETE request
    delete: (url: string, options: FetchOptions = {}) => {
      return fetchWithCache(url, { method: 'DELETE', ...options })
    },
    
    // Clear cache
    clearCache: () => {
      ssrCache.clear()
    }
  }

  // Make the API available throughout the app
  nuxtApp.provide('api', api)
}) as Plugin

// Type definitions for better TypeScript support
declare module 'nuxt/app' {
  interface NuxtApp {
    $api: {
      get: (url: string, options?: FetchOptions) => Promise<any>
      post: (url: string, data?: Record<string, any>, options?: FetchOptions) => Promise<any>
      put: (url: string, data?: Record<string, any>, options?: FetchOptions) => Promise<any>
      delete: (url: string, options?: FetchOptions) => Promise<any>
      clearCache: () => void
    }
  }
}
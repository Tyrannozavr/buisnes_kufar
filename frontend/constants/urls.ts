// API URLs
export const API_URLS = {
  // Companies
  COMPANIES: '/v1/companies',
  COMPANIES_LATEST: '/v1/companies/latest',
  
  // Announcements
  ANNOUNCEMENTS: '/v1/announcements',
  ANNOUNCEMENTS_LATEST: '/v1/announcements',
  ANNOUNCEMENTS_CATEGORIES: '/v1/announcements/categories/list',
  
  // Products
  PRODUCTS: '/api/products',
  
  // Services
  SERVICES: '/api/services',
  
  // Auth
  AUTH_LOGIN: '/api/auth/login',
  AUTH_REGISTER: '/api/auth/register',
  AUTH_LOGOUT: '/api/auth/logout',
  
  // Profile
  PROFILE: '/api/profile',
  
  // Categories
  CATEGORIES: '/api/categories',
  
  // Locations
  LOCATIONS_COUNTRIES: '/api/locations/countries',
  LOCATIONS_REGIONS: '/api/locations/regions',
  LOCATIONS_CITIES: '/api/locations/cities',
  
  // Chats
  CHATS: '/api/chats',
  
  // News
  NEWS: '/api/news',
  
  // Reviews
  REVIEWS: '/api/reviews'
} as const 
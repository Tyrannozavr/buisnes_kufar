// API URLs
export const API_URLS = {
	//Purchases
	CREATE_DEAL: '/api/v1/purchases/deals',
	GET_BUYER_DEALS: '/api/v1/purchases/buyer/deals', 
	GET_SELLER_DEALS: '/api/v1/purchases/seller/deals',
	GET_DEAL_BY_ID: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}`,
	PUT_DEAL_BY_ID: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}`,
	CREATE_BILL: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}/bill`,
	CREATE_CONTRACT: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}/contract`,
	CREATE_SUPPLY_CONTRACT: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}/supply-contract`,
	CREATE_ORDER_FROM_CHECKOUT: '/api/v1/purchases/checkout',
	GET_UNITS_MEASUREMENT: '/api/v1/purchases/units',
	DELETE_DEAL_BY_ID: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}`,

  // Documents
  GET_DOCUMENTS_BY_DEAL_ID: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}/documents`,
  UPLOAD_DOCUMENT_BY_DEAL_ID: (deal_id: number) => `/api/v1/purchases/deals/${deal_id}/documents`,
  DOWNLOAD_DOCUMENT: (deal_id: number, document_id: number) => `/api/v1/purchases/deals/${deal_id}/documents/${document_id}/download`,
  DELETE_DOCUMENT: (deal_id: number, document_id: number) => `/api/v1/purchases/deals/${deal_id}/documents/${document_id}`,

  // Companies
  COMPANIES: '/v1/companies/',
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

export const AUTH_URLS = {
  // Регистрация
  REGISTER_STEP1: '/v1/auth/register/step1',
  REGISTER_STEP2: '/v1/auth/register/step2',
  VERIFY_TOKEN: '/v1/auth/verify-token',
  VERIFY_REGISTRATION_TOKEN: '/v1/auth/registration/verify-token',
  
  // Авторизация
  LOGIN: '/v1/auth/login',
  
  // Смена пароля
  CHANGE_PASSWORD: '/v1/auth/change-password',
  
  // Смена email
  REQUEST_EMAIL_CHANGE: '/v1/auth/request-email-change',
  CONFIRM_EMAIL_CHANGE: '/v1/auth/confirm-email-change',
  
  // Сброс пароля
  REQUEST_PASSWORD_RESET: '/v1/auth/request-password-reset',
  CONFIRM_PASSWORD_RESET: '/v1/auth/confirm-password-reset',
  
  // Компания
  COMPANY_ME: '/v1/company/me'
} as const 
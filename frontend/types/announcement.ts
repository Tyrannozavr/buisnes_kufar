export interface CompanyInfo {
  id: number;
  name: string;
  logo?: string;
  logo_url?: string;
}

export interface Announcement {
  id: number;
  company_id: number;
  title: string;
  content: string;
  images: string[];
  image_urls: string[];
  image_url?: string;
  created_at: string;
  updated_at: string;
  category: string;
  published: boolean;
  company?: CompanyInfo;
  notifications?: {
    partners: boolean;
    customers: boolean;
    suppliers: boolean;
    sent: boolean;
  };
  company_name?: string;
  company_logo?: string;
  date?: string;
  topic?: string;
  image?: string;
}

export interface AnnouncementFormData {
  title: string;
  content: string;
  images: string[];
  image_urls: string[];
  category: string;
  published?: boolean;
  notifications?: {
    partners: boolean;
    customers: boolean;
    suppliers: boolean;
  };
}

export interface AnnouncementCard {
  id: string;
  image: string;
  title: string;
  date: string;
}

export interface AnnouncementCategory {
  id: string;
  name: string;
  description: string;
}

export interface AnnouncementListResponse {
  announcements: Announcement[];
  total: number;
  page: number;
  per_page: number;
}
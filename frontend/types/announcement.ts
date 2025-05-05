export interface Announcement {
  id: string;
  companyId: string;
  title: string;
  content: string;
  status: 'draft' | 'pending' | 'published' | 'rejected';
  createdAt: string;
  updatedAt: string;
  category: 'product' | 'service' | 'promotion' | 'partnership' | 'other';
  images: string[];
  published: boolean;
}

export interface AnnouncementFormData {
  title: string;
  content: string;
  images: string[];
}
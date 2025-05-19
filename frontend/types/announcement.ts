export interface Announcement {
  id: string;
  companyId: number;
  title: string;
  content: string;
  images: string[];
  createdAt: string;
  updatedAt: string;
  category: string;
  published: boolean;
  notifications?: {
    partners: boolean;
    customers: boolean;
    suppliers: boolean;
    sent: boolean;
  };
  companyName: string;
  companyLogo: string;
  date: string;
  topic: string;
}

export interface AnnouncementFormData {
  title: string;
  content: string;
  images: string[];
  category: string;
}
import type { PartnerCompany } from '~/types/company'

// Mock data for buyers
const buyers: PartnerCompany[] = [
  {
    fullName: 'ООО "Покупатель 1"',
    slug: 'buyer-1',
    logo: 'https://yt3.googleusercontent.com/ytc/AIdro_kris1qXf6JIrXdVIUHrN5Fxv2t1yKx8fT6TtGQURWXag=s900-c-k-c0x00ffffff-no-rj',
    businessType: 'Розничная торговля',
    country: 'Россия',
    region: 'Московская область',
    city: 'Москва'
  },
  {
    fullName: 'ООО "Покупатель 2"',
    slug: 'buyer-2',
    logo: 'https://yt3.googleusercontent.com/ytc/AIdro_kris1qXf6JIrXdVIUHrN5Fxv2t1yKx8fT6TtGQURWXag=s900-c-k-c0x00ffffff-no-rj',
    businessType: 'Оптовая торговля',
    country: 'Россия',
    region: 'Ленинградская область',
    city: 'Санкт-Петербург'
  }
]

// Helper function to get random items from array
function getRandomItems<T>(array: T[], count: number): T[] {
  const shuffled = [...array].sort(() => 0.5 - Math.random())
  return shuffled.slice(0, count)
}

export default defineEventHandler(async (event) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000))

  // Return random buyers
  return getRandomItems(buyers, 4)
}) 
import type { PartnerCompany } from '~/types/company'

// Mock data for suppliers
const suppliers: PartnerCompany[] = [
  {
    fullName: 'ООО "Поставщик 1"',
    slug: 'supplier-1',
    logo: 'https://avatars.mds.yandex.net/i?id=0b8872628f8a5da597f4fe16698f580a_l-10150478-images-thumbs&n=13',
    businessType: 'Производство электроники',
    country: 'Россия',
    region: 'Московская область',
    city: 'Москва'
  },
  {
    fullName: 'ООО "Поставщик 2"',
    slug: 'supplier-2',
    logo: 'https://avatars.mds.yandex.net/i?id=0b8872628f8a5da597f4fe16698f580a_l-10150478-images-thumbs&n=13',
    businessType: 'Производство мебели',
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

  // Return random suppliers
  return getRandomItems(suppliers, 4)
}) 
import { defineEventHandler } from 'h3'
import type {Manufacturer} from "~/types/company";



// Mock data for manufacturers
const manufacturers: Manufacturer[] = [
  {
    id: '1',
    logo: 'https://banner2.cleanpng.com/20181124/av/kisspng-comcast-business-organization-computer-icons-email-5bf8ef2b040795.9053466915430408110165.jpg',
    description: 'Ведущий производитель промышленного оборудования в России',
    tradeActivity: 'Покупатель и продавец',
    country: 'Россия',
    region: 'Московская область',
    city: 'Москва',
    name: 'Manufacturer A',
  },
  {
    id: '2',
    logo: 'https://banner2.cleanpng.com/20181124/av/kisspng-comcast-business-organization-computer-icons-email-5bf8ef2b040795.9053466915430408110165.jpg',
    description: 'Комплексные строительные услуги под ключ',
    name: 'Manufacturer B',
    country: 'Россия',
    region: 'Санкт-Петербург',
    city: 'Санкт-Петербург',
    tradeActivity: 'Продавец',

  },
  {
    id: '3',
    logo: 'https://banner2.cleanpng.com/20181124/av/kisspng-comcast-business-organization-computer-icons-email-5bf8ef2b040795.9053466915430408110165.jpg',
    tradeActivity: 'Покупатель и продавец',
    country: 'Россия',
    region: 'Новосибирская область',
    city: 'Новосибирск',
    name: 'Manufacturer C',
    description: 'Innovative solutions for automation',

  }
]

export default defineEventHandler(() => {
  // Simulate a slight delay to mimic real API behavior
  return new Promise<Manufacturer[]>((resolve) => {
    setTimeout(() => {
      resolve(manufacturers)
    }, 300)
  })
})

import { defineEventHandler } from 'h3'

// Define a simple manufacturer type
interface Manufacturer {
  id: string
  name: string
  description?: string
  website?: string
  foundedYear?: number
}

// Mock data for manufacturers
const manufacturers: Manufacturer[] = [
  {
    id: '1',
    name: 'Manufacturer A',
    description: 'Leading manufacturer of industrial equipment',
    website: 'www.manufacturer-a.com',
    foundedYear: 1995
  },
  {
    id: '2',
    name: 'Manufacturer B',
    description: 'Specialized in electronic components',
    website: 'www.manufacturer-b.com',
    foundedYear: 2005
  },
  {
    id: '3',
    name: 'Manufacturer C',
    description: 'Innovative solutions for automation',
    website: 'www.manufacturer-c.com',
    foundedYear: 2010
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

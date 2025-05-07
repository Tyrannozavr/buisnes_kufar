import { defineEventHandler } from 'h3'
import { companies } from '../companies.get'
import type { PartnerCompany } from '~/types/company'

// Function to get random items from an array
const getRandomItems = <T>(array: T[], count: number): T[] => {
    const shuffled = [...array].sort(() => 0.5 - Math.random())
    return shuffled.slice(0, count)
}


export default defineEventHandler(() => {
    // Get 4 random companies
    const randomCompanies = getRandomItems(companies, 4)

    // Map to include only the required fields
    const partners: PartnerCompany[] = randomCompanies.map(company => ({
        fullName: company.fullName,
        slug: company.slug,
        logo: company.logo,
        businessType: company.businessType,
        country: company.country,
        region: company.region,
        city: company.city
    }))

    // Simulate a slight delay to mimic real API behavior
    return new Promise<PartnerCompany[]>((resolve) => {
        setTimeout(() => {
            resolve(partners)
        }, 200)
    })
})
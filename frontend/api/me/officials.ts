import type{ CompanyOfficial, CompanyOfficialBase } from '~/types/company'

export const AUTH_API = {
    OFFICIALS: '/v1/company/me/officials',
    OFFICIAL: '/v1/company/me/officials/{official_id}',
} as const

export const useOfficialsApi = () => {
    const { $api } = useNuxtApp()

    // Get all officials
    const getOfficials = async (): Promise<CompanyOfficial[]> => {
        return await $api.get(AUTH_API.OFFICIALS)
    }

    // Create a new official
    const createOfficial = async (officialData: CompanyOfficialBase): Promise<CompanyOfficial> => {
        return await $api.post(AUTH_API.OFFICIALS, officialData)
    }

    // Update an existing official
    const updateOfficial = async (officialId: number, officialData: Partial<CompanyOfficialBase>): Promise<CompanyOfficial> => {
        const url = AUTH_API.OFFICIAL.replace('{official_id}', officialId.toString())
        return await $api.put(url, officialData)
    }

    // Delete an official
    const deleteOfficial = async (officialId: number): Promise<void> => {
        const url = AUTH_API.OFFICIAL.replace('{official_id}', officialId.toString())
        await $api.delete(url)
    }

    // Get a single official by ID
    const getOfficialById = async (officialId: number): Promise<CompanyOfficial> => {
        const url = AUTH_API.OFFICIAL.replace('{official_id}', officialId.toString())
        return await $api.get(url)
    }

    return {
        getOfficials,
        createOfficial,
        updateOfficial,
        deleteOfficial,
        getOfficialById
    }
}
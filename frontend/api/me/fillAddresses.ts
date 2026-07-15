import type {
	CompanyFillAddress,
	CompanyFillAddressCreate,
	CompanyFillAddressUpdate,
	FillAddressKind,
} from '~/types/fillAddress'

const BASE = '/v1/company/me/fill-addresses'

export const useFillAddressesApi = () => {
	const { $api } = useNuxtApp()

	const listFillAddresses = async (kind?: FillAddressKind): Promise<CompanyFillAddress[]> => {
		const query = kind ? `?kind=${kind}` : ''
		return await $api.get(`${BASE}${query}`)
	}

	const createFillAddress = async (
		data: CompanyFillAddressCreate,
	): Promise<CompanyFillAddress> => {
		return await $api.post(BASE, data)
	}

	const updateFillAddress = async (
		id: number,
		data: CompanyFillAddressUpdate,
	): Promise<CompanyFillAddress> => {
		return await $api.put(`${BASE}/${id}`, data)
	}

	const setFillAddressDefault = async (id: number): Promise<CompanyFillAddress> => {
		return await $api.patch(`${BASE}/${id}/default`)
	}

	const deleteFillAddress = async (id: number): Promise<void> => {
		await $api.delete(`${BASE}/${id}`)
	}

	return {
		listFillAddresses,
		createFillAddress,
		updateFillAddress,
		setFillAddressDefault,
		deleteFillAddress,
	}
}

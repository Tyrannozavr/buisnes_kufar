import type {
	CompanyVehicle,
	CompanyVehicleCreate,
	CompanyDriver,
	CompanyDriverCreate,
} from '~/types/fleet'

const VEHICLES = '/v1/company/me/vehicles'
const DRIVERS = '/v1/company/me/drivers'

export const useFleetApi = () => {
	const { $api } = useNuxtApp()

	const listVehicles = async () =>
		(await $api.get(VEHICLES)) as CompanyVehicle[]

	const createVehicle = async (data: Partial<CompanyVehicleCreate>) =>
		(await $api.post(VEHICLES, data)) as CompanyVehicle

	const updateVehicle = async (id: number, data: Partial<CompanyVehicleCreate>) =>
		(await $api.put(`${VEHICLES}/${id}`, data)) as CompanyVehicle

	const deleteVehicle = async (id: number) =>
		await $api.delete(`${VEHICLES}/${id}`)

	const listDrivers = async () =>
		(await $api.get(DRIVERS)) as CompanyDriver[]

	const createDriver = async (data: Partial<CompanyDriverCreate>) =>
		(await $api.post(DRIVERS, data)) as CompanyDriver

	const updateDriver = async (id: number, data: Partial<CompanyDriverCreate>) =>
		(await $api.put(`${DRIVERS}/${id}`, data)) as CompanyDriver

	const deleteDriver = async (id: number) =>
		await $api.delete(`${DRIVERS}/${id}`)

	return {
		listVehicles,
		createVehicle,
		updateVehicle,
		deleteVehicle,
		listDrivers,
		createDriver,
		updateDriver,
		deleteDriver,
	}
}

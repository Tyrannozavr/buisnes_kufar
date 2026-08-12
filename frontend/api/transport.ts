import type {
	CargoData,
	CargoDetail,
	Shipment,
	ShipmentRequest,
	TransportDetail,
	TransportDictionaries,
	TransportSearchFilters,
	TransportVehicleResult,
} from '~/types/transport'

const BASE = '/v1/transport'

export const useTransportApi = () => {
	const { $api } = useNuxtApp()

	return {
		getDictionaries: () => $api.get('/v1/company/fleet-dictionaries') as Promise<TransportDictionaries>,
		search: (filters: TransportSearchFilters) =>
			$api.post(`${BASE}/search`, filters) as Promise<{
				vehicles: TransportVehicleResult[]
				requests_created?: number
				requests_updated?: number
			}>,
		listRequests: () => $api.get(`${BASE}/requests`) as Promise<ShipmentRequest[]>,
		activateRequest: (id: number) => $api.post(`${BASE}/requests/${id}/activate`) as Promise<ShipmentRequest>,
		acceptRequest: (id: number) => $api.post(`${BASE}/requests/${id}/accept`) as Promise<Shipment>,
		sendVehicleRequest: (id: number) => $api.post(`${BASE}/vehicles/${id}/send-request`) as Promise<ShipmentRequest>,
		listShipments: () => $api.get(`${BASE}/shipments`) as Promise<Shipment[]>,
		getCargo: (id: number) =>
			$api.get(`${BASE}/shipments/${id}/cargo`) as Promise<CargoDetail>,
		getTransport: (id: number) =>
			$api.get(`${BASE}/shipments/${id}/transport`) as Promise<TransportDetail>,
		updateCargo: (id: number, data: CargoData) =>
			$api.patch(`${BASE}/shipments/${id}/cargo`, data) as Promise<Shipment>,
		updateTransport: (id: number, data: { vehicle_id?: number | null, driver_id?: number | null }) =>
			$api.patch(`${BASE}/shipments/${id}/transport`, data) as Promise<Shipment>,
		updateDeal: (id: number, deal_id: number) =>
			$api.patch(`${BASE}/shipments/${id}/deal`, { deal_id }) as Promise<Shipment>,
		listVehicleFavorites: () => $api.get(`${BASE}/favorites/vehicles`) as Promise<TransportVehicleResult[]>,
		listVehicleFavoriteIds: () =>
			$api.get(`${BASE}/favorites/vehicles/ids`) as Promise<{ ids: number[] }>,
		addVehicleFavorite: (id: number) => $api.post(`${BASE}/favorites/vehicles/${id}`),
		removeVehicleFavorite: (id: number) => $api.delete(`${BASE}/favorites/vehicles/${id}`),
		listRequestFavorites: () => $api.get(`${BASE}/favorites/requests`) as Promise<ShipmentRequest[]>,
		listRequestFavoriteIds: () =>
			$api.get(`${BASE}/favorites/requests/ids`) as Promise<{ ids: number[] }>,
		addRequestFavorite: (id: number) => $api.post(`${BASE}/favorites/requests/${id}`),
		removeRequestFavorite: (id: number) => $api.delete(`${BASE}/favorites/requests/${id}`),
	}
}

import type { CompanyDriver, CompanyVehicle, FleetLocation } from '~/types/fleet'

export interface TransportDictionaries {
	body_types: string[]
	loading_methods: string[]
	adr_classes: string[]
}

export interface TransportSearchFilters {
	body_types: string[]
	loading_methods: string[]
	adr_classes: string[]
	capacity_min_kg?: number | null
	capacity_max_kg?: number | null
	cargo_weight_kg?: number | null
	volume_min_m3?: number | null
	volume_max_m3?: number | null
	cargo_volume_m3?: number | null
	partial_load: boolean
	load_date?: string | null
	from_locations: FleetLocation[]
	to_locations: FleetLocation[]
}

export interface TransportCompany {
	id: number
	name: string
	type?: string | null
	inn?: string | null
	legal_address?: string | null
	phone?: string | null
	email?: string | null
}

export interface TransportVehicleResult extends Pick<CompanyVehicle,
	'id' | 'company_id' | 'name' | 'plate_number' | 'trailer_plate_number' |
	'trailer_length_m' | 'trailer_width_m' | 'trailer_height_m' | 'load_date' |
	'body_type' | 'capacity_tons' | 'volume_m3' | 'loading_methods' |
	'adr_classes' | 'from_locations' | 'to_locations' | 'partial_load' |
	'partial_load_weight_kg' | 'partial_load_volume_m3'> {
	company: TransportCompany
}

export interface ShipmentRequest {
	id: number
	client_company_id: number
	carrier_company_id: number
	status: string
	is_highlighted: boolean
	search_filters: TransportSearchFilters
	matched_vehicle_ids: number[]
	created_at: string
	updated_at: string
	activated_at?: string | null
	expires_at: string
}

export interface Shipment {
	id: number
	number: string
	year: number
	client_company_id: number
	carrier_company_id: number
	request_id: number
	deal_id?: number | null
	cargo_data: CargoData
	vehicle_id?: number | null
	driver_id?: number | null
	transport_snapshot: Record<string, unknown>
	created_at: string
	updated_at: string
}

export interface CargoData {
	loading_date?: string | null
	loading_time?: string | null
	loading_address?: string | null
	unloading_date?: string | null
	unloading_time?: string | null
	unloading_address?: string | null
	route?: string | null
	contact_loading?: Record<string, unknown> | null
	contact_unloading?: Record<string, unknown> | null
	cargo_name?: string | null
	transport_conditions?: string | null
	net_weight?: number | null
	gross_weight?: number | null
	places_count?: number | null
	volume?: number | null
	marking?: string | null
	packaging_type?: string | null
	packaging?: string | null
	seal?: string | null
	rate?: number | null
	payment_terms?: string | null
	declared_value?: number | null
	dangerous_goods?: string[] | null
	attached_documents?: unknown[] | null
	identity_document_requisites?: string | null
}

export type { CompanyDriver, CompanyVehicle }

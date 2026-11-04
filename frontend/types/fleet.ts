export interface CompanyVehicle {
	id: number
	company_id: number
	name: string
	plate_number?: string | null
	trailer_plate_number?: string | null
	trailer_length_m?: number | null
	trailer_width_m?: number | null
	trailer_height_m?: number | null
	load_date?: string | null
	body_type?: string | null
	loading_methods: string[]
	adr_classes: string[]
	from_locations: FleetLocation[]
	to_locations: FleetLocation[]
	partial_load: boolean
	partial_load_weight_kg?: number | null
	partial_load_volume_m3?: number | null
	vehicle_type?: string | null
	capacity_tons?: number | null
	volume_m3?: number | null
	notes?: string | null
	is_active: boolean
}

export interface FleetLocation {
	name: string
	[key: string]: unknown
}

export interface CompanyDriver {
	id: number
	company_id: number
	full_name: string
	phone?: string | null
	license_number?: string | null
	inn?: string | null
	notes?: string | null
	is_active: boolean
}

export type CompanyVehicleCreate = Omit<CompanyVehicle, 'id' | 'company_id'>
export type CompanyDriverCreate = Omit<CompanyDriver, 'id' | 'company_id'>

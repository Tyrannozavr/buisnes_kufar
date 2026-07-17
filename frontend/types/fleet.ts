export interface CompanyVehicle {
	id: number
	company_id: number
	name: string
	plate_number?: string | null
	vehicle_type?: string | null
	capacity_tons?: number | null
	volume_m3?: number | null
	notes?: string | null
	is_active: boolean
}

export interface CompanyDriver {
	id: number
	company_id: number
	full_name: string
	phone?: string | null
	license_number?: string | null
	notes?: string | null
	is_active: boolean
}

export type CompanyVehicleCreate = Omit<CompanyVehicle, 'id' | 'company_id'>
export type CompanyDriverCreate = Omit<CompanyDriver, 'id' | 'company_id'>

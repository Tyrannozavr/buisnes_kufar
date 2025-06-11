export interface Country {
  id: string
  name: string
  code: string
}

export interface FederalDistrict {
  id: string
  name: string
  countryId: string
}

export interface Region {
  id: string
  name: string
  federalDistrictId: string
}

export interface City {
  id: string
  name: string
  regionId: string
}

export interface LocationItem {
  label: string
  value: string
}

export interface LocationResponse {
  items: LocationItem[]
  total: number
}

export interface CityInfo {
  id: number
  name: string
  area?: number
  telcod?: string
  latitude?: number
  longitude?: number
  time_zone?: number | string
  english?: string
  rajon?: number | string
  country?: string
  sound?: string
  level?: number | string
  iso?: string
  vid?: number | string
  full_name?: string
}

export interface CitySearchResponse {
  items: CityInfo[]
  total: number
}
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
  data: LocationItem[]
} 
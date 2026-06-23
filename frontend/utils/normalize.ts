/**
 * @param isoDate: string
 * @param style2: boolean | undefined
 * @returns string
 * @description normalize date from ISO to "01.01.2026"
 * @description style2 normalize date from ISO to "«01» января 2026"
 * @example "2026-02-06T08:20:07.011535" -> "06.02.2026"
 */
export const normalizeDate = (isoDate: string, style2?: boolean) => {
	if (!isoDate) return "";

	const month = (monthNumber: string): string => {
		const dictionary = new Map<string, string>([
			['01', 'января'],
			['02', 'февраля'],
			['03', 'марта'],
			['04', 'апреля'],
			['05', 'мая'],
			['06', 'июня'],
			['07', 'июля'],
			['08', 'августа'],
			['09', 'сентября'],
			['10', 'октября'],
			['11', 'ноября'],
			['12', 'декабря']
		])
		return dictionary.get(monthNumber) ?? '___________'
	}

	if (style2) {
		const style2Date = `«${isoDate.slice(8, 10)}» ${month(isoDate.slice(5, 7))} ${isoDate.slice(0, 4)}`
		return style2Date
	}

	const normalizedDate = `${isoDate.slice(8, 10)}.${isoDate.slice(5, 7)}.${isoDate.slice(0, 4)}`
  return normalizedDate
};

/** 
* @param url string
* @returns string
* @description normalize to avoid "/api/api/..." 
* @example "/api/api/..." -> "/api/..."
*/
export const normalizeApiPath = (url: string) => (url.startsWith('/api/') ? url.replace(/^\/api/, '') : url)


/**
* @param price: number
* @returns string
* @description normalize price to "1,200.00"
* @example 1200 -> "1,200.00"
*/
export const normalizePrice = (price: number) => {
	return price.toLocaleString('en', {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	})
}

/**
* @param rawValue: unknown
* @returns number | undefined
* @description normalize vat rate to number
* @example null -> undefined
* @example undefined -> undefined
* @example "5" -> 5
* @example {value: 5} -> 5
* @example {value: "5"} -> 5
*/
export const normalizeVatRate = (rawValue: unknown): number | undefined => {
  if (rawValue === null || rawValue === undefined) return undefined

  // Nuxt UI can emit either primitive value or the whole item object (often as a Proxy)
  if (typeof rawValue === 'number') return rawValue

  if (typeof rawValue === 'string') {
    const parsed = Number(rawValue)
    return Number.isFinite(parsed) ? parsed : undefined
  }

  if (typeof rawValue === 'object' && 'value' in (rawValue as Record<string, unknown>)) {
    const value = (rawValue as { value?: unknown }).value
		if (typeof value === 'number') return value
		
    const parsed = typeof value === 'string' ? Number(value) : Number(value)
    return Number.isFinite(parsed) ? parsed : undefined
  }

  return undefined
}

/**
 * @param rawValue unknown
 * @returns string
 * @description normalize specification number to plain numeric format (e.g. "0005" -> "5")
 */
export const normalizeSpecificationNumber = (rawValue: unknown): string => {
	if (rawValue === null || rawValue === undefined) return ''

	const value = String(rawValue).trim()
	if (!value) return ''
	if (!/^\d+$/.test(value)) return value

	return String(Number(value))
}


/**
 * @param fullName string
 * @example Ivanov Ivan Ivanovich -> Ivanov I.I.
 * @example Ivanov Ivan -> Ivanov I.
 * @returns string
 */
export const normalizeName = (fullName: string): string => {
	const arr = fullName.split(/\s+/)

	let q = 0
	arr.forEach(el => q += 1)

	switch (q) {
		case q = 2:
			return `${arr[0]} ${arr[1]?.slice(0, 1) ?? ""}.`
		case q = 3:
			return `${arr[0]} ${arr[1]?.slice(0, 1) ?? ""}.${ arr[2]?.slice(0, 1) ?? "" }. `
	}

	return fullName
}
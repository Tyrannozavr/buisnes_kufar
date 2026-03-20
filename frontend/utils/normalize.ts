/**
 * @param isoDate: string
 * @returns string
 * @description normalize date from ISO to "01.01.2026"
 * @example "2026-02-06T08:20:07.011535" -> "06.02.2026"
 */
export const normalizeDate = (isoDate: string) => {
  if (!isoDate) return "";
  const normalizedDate = `${isoDate.slice(8, 10)}.${isoDate.slice(5, 7)}.${isoDate.slice(0, 4)}`;

  return normalizedDate;
};

/** 
* @param url: string
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
	return price.toLocaleString('en')
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
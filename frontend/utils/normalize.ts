/* 
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

/* 
* @param url: string
* @returns string
* @description normalize to avoid "/api/api/..." 
* @example "/api/api/..." -> "/api/..."
*/
export const normalizeApiPath = (url: string) => (url.startsWith('/api/') ? url.replace(/^\/api/, '') : url)


/* 
* @param price: number
* @returns string
* @description normalize price to "1,200.00"
* @example 1200 -> "1,200.00"
*/
export const normalizePrice = (price: number) => {
	return price.toLocaleString('en')
}
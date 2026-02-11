// ISO date format: "2026-02-06T08:20:07.011535"
//normalize date from ISO to "01.01.2026"
export const normalizeDate = (isoDate: string) => {
  if (!isoDate) return "";
  const normalizedDate = `${isoDate.slice(8, 10)}.${isoDate.slice(5, 7)}.${isoDate.slice(0, 4)}`;

  return normalizedDate;
};

	//normalize to avoid "/api/api/..."
export const normalizeApiPath = (url: string) => (url.startsWith('/api/') ? url.replace(/^\/api/, '') : url)
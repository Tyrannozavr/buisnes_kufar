/** Убирает тип организации из начала названия, если он уже там есть (ООО + «ООО …»). */
export function stripLeadingOrgType(companyName: string, companyType?: string): string {
	const name = companyName.trim()
	const type = companyType?.trim()
	if (!type || !name) return name
	if (name.toUpperCase().startsWith(type.toUpperCase())) {
		return name.slice(type.length).trim()
	}
	return name
}

/** Адрес для строки реквизитов: индекс не дублируем, если уже в legalAddress. */
export function formatLegalAddressForParty(index?: string, legalAddress?: string): string {
	const addr = (legalAddress ?? '').trim()
	const idx = (index ?? '').trim()
	if (!addr) return idx
	if (idx && (addr.startsWith(idx) || addr.startsWith(`${idx},`))) {
		return addr
	}
	if (idx) return `${idx}, ${addr}`
	return addr
}

export type PartyLineFields = {
	companyType?: string
	companyName?: string
	inn?: number | string
	kpp?: string
	index?: string
	legalAddress?: string
}

/** Строка «Поставщик/Покупатель» по §5 ТЗ. */
export function formatCompanyPartyLine(party: PartyLineFields | undefined): string {
	if (!party?.companyName) return ''
	const type = party.companyType?.trim()
	const shortName = stripLeadingOrgType(party.companyName, type)
	const fullName = type ? `${type} ${shortName}`.trim() : shortName
	const address = formatLegalAddressForParty(party.index, party.legalAddress)
	return [fullName, party.inn, party.kpp, address]
		.filter((part) => part !== '' && part !== undefined && part !== null)
		.join(', ')
}

/** «Получатель» в верхней таблице: тип + название без дубля типа. */
export function formatCompanyRecipientLine(party: Pick<PartyLineFields, 'companyType' | 'companyName'> | undefined): string {
	if (!party?.companyName) return ''
	const type = party.companyType?.trim()
	const shortName = stripLeadingOrgType(party.companyName, type)
	return type ? `${type} ${shortName}`.trim() : shortName
}

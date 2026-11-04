import {
	formatCompanyRecipientLine,
	formatLegalAddressForParty,
} from '~/utils/companyPartyLine'
import {
	emptyCarriageParty,
	type CarriagePartyPayload,
} from '~/utils/carriageContractDefaults'

/** Полное юр. название без «ООО» + «Общество с ограниченной…». */
export const legalPartyName = (company: Record<string, any>): string => {
	const companyType = String(company.type || company.company_type || '')
	const raw = String(company.full_name || company.fullName || company.name || '')
	if (/общество с ограниченной ответственностью/i.test(raw)) return raw
	if (/индивидуальный предприниматель/i.test(raw)) return raw
	if (/акционерное общество/i.test(raw)) return raw
	return formatCompanyRecipientLine({ companyType, companyName: raw }) || raw
}

const foundationFromOfficial = (official: Record<string, any>) => {
	const rawKind = String(official.base_document || official.baseDocument || '').trim()
	const rawTitle = String(
		official.base_document_name || official.baseDocumentName || '',
	).trim()
	let foundationKind = rawKind || 'Устава'
	if (/^устав$/i.test(foundationKind)) foundationKind = 'Устава'
	if (/^доверенность$/i.test(foundationKind)) foundationKind = 'доверенности'
	const kindStem = foundationKind.replace(/а$/i, '').toLowerCase()
	const titleLooksSame =
		!rawTitle ||
		rawTitle.toLowerCase() === rawKind.toLowerCase() ||
		rawTitle.toLowerCase() === foundationKind.toLowerCase() ||
		rawTitle.toLowerCase() === kindStem ||
		/^устав$/i.test(rawTitle)
	return {
		foundationKind,
		foundationTitle: titleLooksSame ? '' : rawTitle,
	}
}

export const partyFromCompany = (
	company: Record<string, any> | null | undefined,
): CarriagePartyPayload => {
	if (!company) return emptyCarriageParty()
	const officials = (company.officials ?? []) as Array<Record<string, any>>
	const first = officials[0] ?? {}
	const companyType = String(company.type || company.company_type || '')
	const index = String(company.index || '')
	const legalRaw = String(company.legal_address || company.legalAddress || '')
	const foundation = foundationFromOfficial(first)
	return {
		fullName: legalPartyName(company),
		companyType,
		city: String(company.city || ''),
		index,
		legalAddress: formatLegalAddressForParty(index, legalRaw),
		inn: String(company.inn ?? ''),
		kpp: String(company.kpp ?? ''),
		ogrn: String(company.ogrn ?? ''),
		accountNumber: String(company.current_account_number || company.accountNumber || ''),
		bankName: String(company.bank_name || company.bankName || ''),
		correspondentBankAccount: String(
			company.correspondent_bank_account || company.correspondentBankAccount || '',
		),
		bic: String(company.bic || ''),
		officialPosition: String(first.position || first.job_title || 'Генеральный директор'),
		officialName: String(first.name || first.full_name || ''),
		foundationKind: foundation.foundationKind,
		foundationTitle: foundation.foundationTitle,
	}
}

export const YELLOW_INPUT_CLASS =
	'bg-yellow-100 border border-yellow-300 rounded px-1 min-w-[5rem] min-h-[1.5rem] disabled:opacity-80'

export const RED_READONLY_CLASS =
	'text-red-600 font-semibold bg-transparent border-0 border-b border-red-300 px-1 min-w-[3rem] text-center cursor-default'

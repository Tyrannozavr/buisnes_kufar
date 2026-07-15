import { getMyCompany } from '~/api/companyOwner'
import type { CompanyResponse } from '~/types/company'
import type { OfficialsResponse } from '~/types/dealResponse'
import type { OfficialBill } from '~/types/bill'
import type { Company as DealCompany } from '~/types/dealState'
import { useUserStore } from '~/stores/user'

const OWNER_POSITION = 'owner'

const REQUISITE_FIELDS: (keyof DealCompany)[] = [
	'companyName',
	'companyType',
	'fullName',
	'legalAddress',
	'productionAddress',
	'index',
	'inn',
	'kpp',
	'ogrn',
	'phone',
	'email',
	'accountNumber',
	'correspondentBankAccount',
	'bankName',
	'bic',
	'vatRate',
]

export const formatOfficialPosition = (position: string) =>
	position === OWNER_POSITION ? 'Владелец' : position

/** CompanyResponse (ЛК) → поля стороны сделки для бланка счёта */
export const mapCompanyResponseToDealParty = (company: CompanyResponse): DealCompany => ({
	companyName: company.name,
	companyType: company.type,
	fullName: company.full_name,
	companyId: company.id,
	phone: company.phone,
	email: company.email,
	legalAddress: company.legal_address,
	productionAddress: company.production_address ?? undefined,
	index: company.index ?? undefined,
	inn: company.inn ? Number(company.inn) || undefined : undefined,
	kpp: company.kpp,
	ogrn: company.ogrn,
	accountNumber: company.current_account_number ?? undefined,
	correspondentBankAccount: company.correspondent_bank_account ?? undefined,
	bankName: company.bank_name ?? undefined,
	bic: company.bic ?? undefined,
	vatRate: company.vat_rate ?? undefined,
})

export const mapCompanyOfficialsToBill = (officials: OfficialsResponse[]): OfficialBill[] =>
	officials.slice(0, 3).map((official) => ({
		id: official.id,
		position: formatOfficialPosition(official.position),
		name: official.full_name,
		isBase: official.is_base,
		baseDocument: official.base_document ?? '',
		baseDocumentName: official.base_document_name ?? '',
	}))

/**
 * Подмешивает реквизиты из ЛК. Пустые значения из ЛК не затирают уже подставленные
 * данные сделки (чтобы «Заполнить данными» работало при частично пустом профиле — §7.4).
 */
export const mergeDealPartyRequisites = (
	current: DealCompany,
	fresh: DealCompany,
): DealCompany => {
	const merged: DealCompany = { ...current }

	for (const field of REQUISITE_FIELDS) {
		const value = fresh[field]
		if (value !== undefined && value !== null && value !== '') {
			merged[field] = value as never
		}
	}

	return merged
}

/**
 * Загрузка актуальных реквизитов компании из ЛК для бланка счёта.
 * Доступно только для компании текущего пользователя.
 */
export function useCompanyBillRequisites(companyId?: MaybeRef<number | undefined>) {
	const userStore = useUserStore()

	const loadBillRequisites = async (
		forCompanyId?: number,
	): Promise<{ party: DealCompany; officials: OfficialBill[] } | null> => {
		const targetId = forCompanyId ?? unref(companyId) ?? userStore.companyId
		if (!targetId || targetId !== userStore.companyId) return null

		try {
			const company = await getMyCompany()
			return {
				party: mapCompanyResponseToDealParty(company),
				officials: mapCompanyOfficialsToBill(company.officials ?? []),
			}
		} catch {
			return null
		}
	}

	return {
		loadBillRequisites,
		mapCompanyResponseToDealParty,
		mapCompanyOfficialsToBill,
		mergeDealPartyRequisites,
	}
}

import type { Company, Official } from "~/types/dealState"

export type SupplyContractParty = "seller" | "buyer" | "contract"

export type SupplyContractFieldKey =
	| "companyName"
	| "companyType"
	| "city"
	| "fullName"
	| "ogrn"
	| "inn"
	| "kpp"
	| "officialName"
	| "legalAddress"
	| "productionAddress"
	| "phone"
	| "email"
	| "paymentTerms"
	| "deliveryTerms"

export interface SupplyContractFieldDefinition {
	key: SupplyContractFieldKey
	label: string
}

export interface InsertedSupplyContractField {
	id: string
	party: SupplyContractParty
	fieldKey: SupplyContractFieldKey
	label: string
}

interface SupplyContractFieldValueContext {
	seller?: Company
	buyer?: Company
	sellerOfficial?: Official
	paymentTerms?: string
	deliveryTerms?: string
}

export const SUPPLY_CONTRACT_FIELD_ATTRIBUTE = "data-supply-contract-field"
export const SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE = "data-supply-contract-label"

export const supplyContractFieldDefinitions: SupplyContractFieldDefinition[] = [
	{ key: "companyName", label: "Название организации" },
	{ key: "companyType", label: "Тип организации" },
	{ key: "city", label: "Город" },
	{ key: "fullName", label: "Полное название организации" },
	{ key: "ogrn", label: "ОРГН" },
	{ key: "inn", label: "ИНН" },
	{ key: "kpp", label: "КПП" },
	{ key: "officialName", label: "ДОЛЖНОСТЬ + ФИО" },
	{ key: "legalAddress", label: "Юридический адрес" },
	{ key: "productionAddress", label: "Адрес производства" },
	{ key: "phone", label: "Телефон" },
	{ key: "email", label: "Электронная почта" },
]

export const supplyContractTermFieldDefinitions: SupplyContractFieldDefinition[] = [
	{ key: "paymentTerms", label: "Срок оплаты" },
	{ key: "deliveryTerms", label: "Срок поставки" },
]

export const supplyContractPartyLabels: Record<SupplyContractParty, string> = {
	seller: "Поставщик",
	buyer: "Покупатель",
	contract: "",
}

const supplyContractFieldsByKey = new Map(
	[...supplyContractFieldDefinitions, ...supplyContractTermFieldDefinitions].map((field) => [field.key, field]),
)

const isSupplyContractParty = (value: string): value is SupplyContractParty =>
	value === "seller" || value === "buyer" || value === "contract"

const isSupplyContractFieldKey = (value: string): value is SupplyContractFieldKey =>
	supplyContractFieldsByKey.has(value as SupplyContractFieldKey)

const normalizeFieldValue = (value: unknown): string => {
	if (value == null) return ""
	return String(value).trim()
}

const getCompanyByParty = (
	party: SupplyContractParty,
	context: SupplyContractFieldValueContext,
): Company | undefined => {
	if (party === "seller") return context.seller
	if (party === "buyer") return context.buyer
	return undefined
}

const parseSupplyContractFieldToken = (
	rawToken: string,
	fallbackLabel?: string | null,
): InsertedSupplyContractField | null => {
	const [party = "", fieldKey = ""] = rawToken.split(".")
	if (!isSupplyContractParty(party) || !isSupplyContractFieldKey(fieldKey)) return null

	return {
		id: `${party}.${fieldKey}`,
		party,
		fieldKey,
		label: fallbackLabel || getSupplyContractFieldLabel(party, fieldKey),
	}
}

export const escapeSupplyContractFieldHtml = (value: string): string =>
	value
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;")

export const getSupplyContractFieldLabel = (
	party: SupplyContractParty,
	fieldKey: SupplyContractFieldKey,
): string => {
	const field = supplyContractFieldsByKey.get(fieldKey)
	const fieldLabel = field?.label ?? fieldKey
	if (party === "contract") return fieldLabel
	return `${fieldLabel} (${supplyContractPartyLabels[party]})`
}

export const getSupplyContractFieldPlaceholder = (label: string): string =>
	`_______________(${label})`

export const resolveSupplyContractFieldValue = (
	party: SupplyContractParty,
	fieldKey: SupplyContractFieldKey,
	context: SupplyContractFieldValueContext,
): string => {
	const company = getCompanyByParty(party, context)

	if (party === "contract") {
		if (fieldKey === "paymentTerms") return normalizeFieldValue(context.paymentTerms)
		if (fieldKey === "deliveryTerms") return normalizeFieldValue(context.deliveryTerms)
		return ""
	}

	if (fieldKey === "officialName") {
		if (party === "seller") {
			const position = normalizeFieldValue(context.sellerOfficial?.position)
			const name = normalizeFieldValue(context.sellerOfficial?.name)
			return [position, name].filter(Boolean).join(" ")
		}

		const ownerName = normalizeFieldValue(company?.ownerName)
		if (!ownerName) return ""
		return `${getSupplyContractFieldPlaceholder("ДОЛЖНОСТЬ")} ${ownerName}`
	}

	const valueByField: Record<Exclude<SupplyContractFieldKey, "officialName" | "paymentTerms" | "deliveryTerms">, unknown> = {
		companyName: company?.companyName,
		companyType: company?.companyType,
		city: company?.city,
		fullName: company?.fullName,
		ogrn: company?.ogrn,
		inn: company?.inn,
		kpp: company?.kpp,
		legalAddress: company?.legalAddress,
		productionAddress: company?.productionAddress,
		phone: company?.phone,
		email: company?.email,
	}

	const companyFieldKey = fieldKey as Exclude<SupplyContractFieldKey, "officialName" | "paymentTerms" | "deliveryTerms">
	return normalizeFieldValue(valueByField[companyFieldKey])
}

export const getSupplyContractFieldDisplayValue = (
	party: SupplyContractParty,
	fieldKey: SupplyContractFieldKey,
	context: SupplyContractFieldValueContext,
): string => {
	const value = resolveSupplyContractFieldValue(party, fieldKey, context)
	if (value) return value
	return getSupplyContractFieldPlaceholder(getSupplyContractFieldLabel(party, fieldKey))
}

export const createSupplyContractFieldTokenHtml = (
	party: SupplyContractParty,
	fieldKey: SupplyContractFieldKey,
	context: SupplyContractFieldValueContext,
): string => {
	const label = getSupplyContractFieldLabel(party, fieldKey)
	const value = getSupplyContractFieldDisplayValue(party, fieldKey, context)

	return `<span ${SUPPLY_CONTRACT_FIELD_ATTRIBUTE}="${party}.${fieldKey}" ${SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE}="${escapeSupplyContractFieldHtml(label)}">${escapeSupplyContractFieldHtml(value)}</span>`
}

export const renderSupplyContractFields = (
	html: string | null | undefined,
	context: SupplyContractFieldValueContext,
): string => {
	if (!html) return ""
	if (!import.meta.client) return html

	const wrapper = document.createElement("div")
	wrapper.innerHTML = html

	wrapper.querySelectorAll<HTMLElement>(`[${SUPPLY_CONTRACT_FIELD_ATTRIBUTE}]`).forEach((element) => {
		const rawToken = element.getAttribute(SUPPLY_CONTRACT_FIELD_ATTRIBUTE) ?? ""
		const parsedToken = parseSupplyContractFieldToken(
			rawToken,
			element.getAttribute(SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE),
		)
		if (!parsedToken) return

		const { party, fieldKey } = parsedToken
		const label = element.getAttribute(SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE)
			|| getSupplyContractFieldLabel(party, fieldKey)
		const value = resolveSupplyContractFieldValue(party, fieldKey, context)

		element.textContent = value || getSupplyContractFieldPlaceholder(label)
	})

	return wrapper.innerHTML
}

export const extractInsertedSupplyContractFields = (
	htmlList: Array<string | null | undefined>,
): InsertedSupplyContractField[] => {
	if (!import.meta.client) return []

	const insertedFields = new Map<string, InsertedSupplyContractField>()

	htmlList.forEach((html) => {
		if (!html) return

		const wrapper = document.createElement("div")
		wrapper.innerHTML = html

		wrapper.querySelectorAll<HTMLElement>(`[${SUPPLY_CONTRACT_FIELD_ATTRIBUTE}]`).forEach((element) => {
			const parsedToken = parseSupplyContractFieldToken(
				element.getAttribute(SUPPLY_CONTRACT_FIELD_ATTRIBUTE) ?? "",
				element.getAttribute(SUPPLY_CONTRACT_FIELD_LABEL_ATTRIBUTE),
			)
			if (!parsedToken || insertedFields.has(parsedToken.id)) return
			insertedFields.set(parsedToken.id, parsedToken)
		})
	})

	return Array.from(insertedFields.values())
}

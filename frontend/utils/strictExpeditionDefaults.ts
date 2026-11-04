export const TRANSPORT_MODES = [
	'Автомобильный',
	'Железнодорожный',
	'Морской',
	'Воздушный',
] as const

export type TransportMode = (typeof TRANSPORT_MODES)[number]

export type StrictPartyLine = {
	fullName: string
	index: string
	legalAddress: string
	inn: string
	/** seller | buyer | other */
	source?: string
	officialName?: string
	officialPosition?: string
}

export const emptyStrictParty = (): StrictPartyLine => ({
	fullName: '',
	index: '',
	legalAddress: '',
	inn: '',
	source: '',
	officialName: '',
	officialPosition: '',
})

export const formatStrictPartyBlock = (p: StrictPartyLine): string => {
	const lines = [
		p.fullName,
		[p.index, p.legalAddress].filter(Boolean).join(', '),
		p.inn ? `ИНН ${p.inn}` : '',
	].filter(Boolean)
	return lines.join('\n')
}

/** Общий payload строгих бланков экспедиции (§5). */
export type StrictExpeditionPayload = {
	shipper: StrictPartyLine
	client: StrictPartyLine
	consignee: StrictPartyLine
	forwarder: StrictPartyLine
	notifyParty: string
	originCountry: string
	readyToShip: string
	transportMode: TransportMode | string
	destination: string
	insurance: string
	commodityCode: string
	marking: string
	placesPackaging: string
	weightGrossNet: string
	volume: string
	value: string
	packageSize: string
	requiredDocs: string
	terms: string
	notes: string
	warehouse: string
	signatureName: string
	signaturePosition: string
}

export const emptyStrictExpeditionPayload = (): StrictExpeditionPayload => ({
	shipper: emptyStrictParty(),
	client: emptyStrictParty(),
	consignee: emptyStrictParty(),
	forwarder: emptyStrictParty(),
	notifyParty: '',
	originCountry: 'Россия',
	readyToShip: '',
	transportMode: 'Автомобильный',
	destination: '',
	insurance: '',
	commodityCode: '',
	marking: '',
	placesPackaging: '',
	weightGrossNet: '',
	volume: '',
	value: '',
	packageSize: '',
	requiredDocs: '',
	terms: '',
	notes: '',
	warehouse: '',
	signatureName: '',
	signaturePosition: '',
})

export type StrictExpeditionDocType =
	| 'forwarder_assignment'
	| 'forwarder_receipt'
	| 'warehouse_receipt'

export const STRICT_EXPEDITION_TITLES: Record<StrictExpeditionDocType, string> = {
	forwarder_assignment: 'ПОРУЧЕНИЕ ЭКСПЕДИТОРУ',
	forwarder_receipt: 'ЭКСПЕДИТОРСКАЯ РАСПИСКА',
	warehouse_receipt: 'СКЛАДСКАЯ РАСПИСКА',
}

export const isStrictExpeditionType = (t: string): t is StrictExpeditionDocType =>
	t === 'forwarder_assignment' ||
	t === 'forwarder_receipt' ||
	t === 'warehouse_receipt'
